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
	"flag"
	"log"
	"os"

	"github.com/knative/pkg/signals"

	"go.uber.org/zap"
)

func main() {
	flag.Parse()

	logger, err := zap.NewProduction()
	if err != nil {
		log.Fatalf("unable to create logger: %v", err)
	}

	a := Adapter{
		Namespace: getRequiredEnv("namespace"),
		SinkURI:   getRequiredEnv("SINK"),
	}

	stopCh := signals.SetupSignalHandler()

	err = a.Start(stopCh)
	if err != nil {
		logger.Fatal("Failed to start the adapter", zap.Error(err))
	}

	logger.Info("exiting...")
}

func getRequiredEnv(envKey string) string {
	val, defined := os.LookupEnv(envKey)
	if !defined {
		log.Fatalf("required environment variable not defined '%s'", envKey)
	}
	return val
}
