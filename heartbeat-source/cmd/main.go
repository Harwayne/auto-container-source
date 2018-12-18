/*
Copyright 2018 The Knative Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package main

import (
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/knative/pkg/cloudevents"
)

type Heartbeat struct {
	Sequence int    `json:"id"`
	Label    string `json:"label"`
}

func main() {
	var period time.Duration
	if p, err := strconv.Atoi(getRequiredEnv("period")); err != nil {
		period = time.Duration(5) * time.Second
	} else {
		period = time.Duration(p) * time.Second
	}

	hb := &Heartbeat{
		Sequence: 0,
		Label:    getRequiredEnv("label"),
	}
	ticker := time.NewTicker(period)
	for {
		hb.Sequence++
		postMessage(getRequiredEnv("SINK"), hb)
		// Wait for next tick
		<-ticker.C
	}
}

func getRequiredEnv(envKey string) string {
	val, defined := os.LookupEnv(envKey)
	if !defined {
		log.Fatalf("required environment variable not defined '%s'", envKey)
	}
	return val
}

// Creates a CloudEvent Context for a given heartbeat.
func cloudEventsContext() *cloudevents.EventContext {
	return &cloudevents.EventContext{
		CloudEventsVersion: cloudevents.CloudEventsVersion,
		EventType:          "dev.knative.source.heartbeats",
		EventID:            uuid.New().String(),
		Source:             "heartbeats-demo",
		EventTime:          time.Now(),
	}
}

func postMessage(target string, hb *Heartbeat) error {
	ctx := cloudEventsContext()

	log.Printf("posting to %q", target)
	// Explicitly using Binary encoding so that Istio, et. al. can better inspect
	// event metadata.
	req, err := cloudevents.Binary.NewRequest(target, hb, *ctx)
	if err != nil {
		log.Printf("failed to create http request: %s", err)
		return err
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Failed to do POST: %v", err)
		return err
	}
	defer resp.Body.Close()
	log.Printf("response Status: %s", resp.Status)
	body, _ := ioutil.ReadAll(resp.Body)
	log.Printf("response Body: %s", string(body))
	return nil
}
