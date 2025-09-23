## Lifted from: https://github.com/alphagov/gcp-cloud-function-python/blob/main/makefile

-include _local/.env
REPO := $(shell basename "$$(pwd)" | tr ' ' '_')
PYTHON_RUNTIME := python$(shell cat .python-version | tr -d '.')
.DEFAULT_GOAL := help
VENDOR_DIR := libs/

## Deploy the codebase to GCP Cloud Functions
deploy:
	gcloud functions deploy $(REPO) \
	--gen2 \
	--project=$(GCP_PROJECT_ID) \
	--region=$(GCP_REGION) \
	--runtime=$(PYTHON_RUNTIME) \
	--memory=512MB \
	--trigger-http \
	--source=. \
	--entry-point=run