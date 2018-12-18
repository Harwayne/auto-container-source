#!/usr/bin/env python

# Copyright 2018 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from http.server import BaseHTTPRequestHandler, HTTPServer
import json


special_container_source_keys = ['serviceAccountName', 'sink']


def make_env(cr_spec):
    env = []
    for key, value in cr_spec.items():
        if key not in special_container_source_keys:
            env.append({
                'name': key,
                'value': json.dumps(value),
            })
    return env


def create_spec(image, cr):
    spec = dict()
    spec['image'] = image
    cr_spec = cr.get('spec', {})
    for key in special_container_source_keys:
        if key in cr_spec:
            spec[key] = cr_spec[key]
    spec['env'] = make_env(cr_spec)
    return spec


def new_container_source(image, cr):
    return {
        'apiVersion': 'sources.eventing.knative.dev/v1alpha1',
        'kind': 'ContainerSource',
        'metadata': {
            'namespace': cr['metadata']['namespace'],
            'name': '%s-%s' % (cr['metadata']['name'], cr['metadata']['uid'])  # TODO GenerateName instead
            #  'generateName': '%s-%s' % (cr['kind'].lower(), cr['metadata']['name'])
        },
        'spec': create_spec(image, cr),
    }


def cr_status(child_container_sources):
    # TODO Add something saying there is no child container source...
    no_status_found = dict()
    for _, container_source in child_container_sources.items():
        return container_source.get('status', no_status_found)
    return no_status_found


def sync_response(image, cr, child_container_sources):
    return {
        'status': cr_status(child_container_sources),
        'children': [
            new_container_source(image, cr),
        ],
    }


def get_image(composite_controller):
    return composite_controller['metadata'].get('annotations', {}).get('AutoContainerSourceImage', None)


class Controller(BaseHTTPRequestHandler):

    def do_POST(self):
        print("Received a request")
        if self.path != "/containerSourceSync":
            print("ERROR: Bad path")
            self.send_error(400, 'Bad path')
            return
        observed = json.loads(self.rfile.read(int(self.headers.get('content-length'))))
        image = get_image(observed['controller'])
        if image is None:
            print("ERROR: No image found")
            self.send_error(500, "No image found on the controller")
            return
        cr = observed['parent']
        child_container_source = observed['children']['ContainerSource.sources.eventing.knative.dev/v1alpha1']

        desired = sync_response(image, cr, child_container_source)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(desired), 'UTF-8'))
        print("returning", json.dumps(desired))


print("Starting HTTP server")
HTTPServer(('', 8080), Controller).serve_forever()
