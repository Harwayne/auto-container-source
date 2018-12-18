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


def sanitize(name):
    return str.replace(name, '.', '-')


def new_composite_controller(crd):
    image = crd['metadata'].get('annotations', {}).get('AutoContainerSourceImage', '')
    if image == '':
        print('ERROR: CRD does not have an image label')
        return None
    return {
        'apiVersion': 'metacontroller.k8s.io/v1alpha1',
        'kind': 'CompositeController',
        'metadata': {
            'name': '%s-cr-reifier' % (sanitize(crd['metadata']['name'])),
            'annotations': {
                'AutoContainerSourceImage': image,
            },
        },
        'spec': {
            'resyncPeriodSeconds': 60,
            'generateSelector': True,
            'parentResource': {
                'apiVersion': '%s/%s' % (crd['spec']['group'], crd['spec']['version']), # TODO Use crd.spec.versions[].name instead.
                'resource': crd['spec']['names']['plural'],
            },
            'childResources': [
                {
                    'apiVersion': 'sources.eventing.knative.dev/v1alpha1',
                    'resource': 'containersources',
                    'updateStrategy': {
                        'method': 'InPlace', # TODO, Recreate?
                    },
                },
            ],
            'hooks': {
                'sync': {
                    'webhook': {
                        'service': {
                            'namespace': 'knative-sources',
                            'name': 'auto-container-cr-reifier-metacontroller',
                        },
                        'path': '/containerSourceSync',
                        'timeout': '10s',
                    },
                },
            },
        },
    }


def crd_sync(crd):
    attachments = []
    composite_controller = new_composite_controller(crd)
    if composite_controller is not None:
        attachments.append(composite_controller)
    return {
        'attachments': attachments,
   }


class Controller(BaseHTTPRequestHandler):

    def do_POST(self):
        print("Received a request")
        if self.path != "/crdSync":
            print("ERROR: Bad path")
            self.send_error(400, 'Bad path')
            return
        observed = json.loads(self.rfile.read(int(self.headers.get('content-length'))))
        desired = crd_sync(observed['object'])

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(desired), 'UTF-8'))
        print("returning", json.dumps(desired))


print("Starting HTTP server")
HTTPServer(('', 8080), Controller).serve_forever()
