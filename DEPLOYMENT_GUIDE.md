# AI Tutor Deployment Guide

This guide provides instructions for running the AI Tutor application locally using Docker and deploying it to Google Cloud Run.

## Prerequisites

**Common for both local and cloud deployment:**
*   **Docker:** Ensure Docker Desktop or Docker Engine is installed and running on your system.
*   **Git:** For cloning the repository.
*   **Project Files:** You should have the AI Tutor project files on your local machine.

**For Google Cloud Run Deployment:**
*   **Google Cloud SDK (gcloud CLI):** Installed and authenticated. ([Installation Guide](https://cloud.google.com/sdk/docs/install))
*   **Google Cloud Project:** A Google Cloud Project set up with billing enabled.
*   **Artifact Registry API Enabled:** Ensure the Artifact Registry API is enabled in your Google Cloud Project.
*   **Artifact Registry Docker Repository:** A Docker repository created in Artifact Registry (e.g., `ai-tutor-repo` in `us-central1`). You can create one using:
    ```bash
    gcloud artifacts repositories create ai-tutor-repo --repository-format=docker --location=us-central1 --description="Docker repository for AI Tutor app"
    ```
*   **Cloud Run API Enabled:** Ensure the Cloud Run API is enabled.
*   **Permissions:** You need appropriate permissions to push to Artifact Registry and deploy to Cloud Run (e.g., Artifact Registry Writer, Cloud Run Admin, Service Account User).

## 1. Environment Variables

The application requires Google API keys. Create a `.env` file in the root of the project with the following content:

```env
GOOGLE_API_KEY=your-api-key
GOOGLE_GENAI_USE_VERTEXAI=False
# Add any other environment variables your application might need
```
**Note:** Replace `your-api-key` with your actual Google API Key. This `.env` file is used for local Docker runs. For Cloud Run, these will be set during deployment.

---

## 2. Running Locally with Docker

This method allows you to run the application in a containerized environment on your local machine.

**Steps:**

1.  **Build the Docker Image:**
    *   Navigate to the project's root directory in your terminal.
    *   If you are on an ARM-based Mac (M1/M2/M3/M4), Docker Desktop's Rosetta 2 emulation will allow you to run `linux/amd64` images. We recommend building for `linux/amd64` for consistency with Cloud Run.
    ```bash
    docker buildx build --platform linux/amd64 -t ai-tutor:latest --load .
    ```
    *   If the `--platform` flag causes issues locally or you prefer a native build for local testing (and are not on an ARM Mac), you can try a standard build:
        ```bash
        # docker build -t ai-tutor:latest .
        ```

2.  **Run the Docker Container:**
    *   Use the `.env` file created earlier for environment variables.
    *   This command maps port 8080 on your host to port 8080 in the container.
    ```bash
    docker run --env-file .env -p 8080:8080 --memory=2g --rm ai-tutor:latest
    ```
    *   `--rm`: Automatically removes the container when it exits.
    *   `--memory=2g`: Sets a memory limit for the container (optional but good practice).
    *   You should see Gunicorn startup logs in your terminal.

3.  **Access the Application:**
    *   Open your web browser and navigate to `http://localhost:8080`.

4.  **View Logs:**
    *   Logs from the application running inside the container will be streamed to your terminal window where you ran `docker run`.

5.  **Stop the Container:**
    *   Press `Ctrl+C` in the terminal where the Docker container is running.

---

## 3. Deploying to Google Cloud Run

This section details how to deploy the application to Google Cloud Run, a serverless platform.

**Deployment Steps:**

1.  **Make Code Changes:**
    *   Modify your application code as needed.

2.  **Rebuild the Docker Image for Cloud Run:**
    *   Cloud Run typically uses `linux/amd64` architecture.
    ```bash
    docker buildx build --platform linux/amd64 -t ai-tutor:latest --load .
    ```

3.  **Tag the Docker Image for Artifact Registry:**
    *   Replace `YOUR_PROJECT_ID` with your Google Cloud Project ID and `ai-tutor-repo` with your Artifact Registry repository name if different.
    ```bash
    docker tag ai-tutor:latest us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai-tutor-repo/ai-tutor:latest
    ```
    ```bash
    # docker tag ai-tutor:latest us-central1-docker.pkg.dev/ai-tutor-461106/ai-tutor-repo/ai-tutor:latest
    ```

4.  **Push the Docker Image to Artifact Registry:**
    *   Ensure you have authenticated Docker to push to Artifact Registry. If not, run:
        ```bash
        gcloud auth configure-docker us-central1-docker.pkg.dev
        ```
    *   Then, push the image:
    ```bash
    docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai-tutor-repo/ai-tutor:latest
    ```
    ```bash
    # docker push us-central1-docker.pkg.dev/ai-tutor-461106/ai-tutor-repo/ai-tutor:latest
    ```

5.  **Deploy the New Image to Cloud Run:**
    *   Replace `YOUR_PROJECT_ID` and `YOUR_GOOGLE_API_KEY`.
    *   It's recommended to change the value of `DUMMY_VAR_TO_FORCE_UPDATE` (e.g., to `trueV2`, `update_$(date +%s)`, etc.) with each deployment to ensure Cloud Run rolls out a new revision.
    ```bash
    gcloud run deploy ai-tutor-service \
      --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai-tutor-repo/ai-tutor:latest \
      --region=us-central1 \
      --platform=managed \
      --memory=2Gi \
      --allow-unauthenticated \
      --set-env-vars=GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY,GOOGLE_GENAI_USE_VERTEXAI=False,DUMMY_VAR_TO_FORCE_UPDATE=true \
      --port=8080
    ```
    

6.  **Verify Deployment:**
    *   Cloud Run will output the Service URL (e.g., `https://ai-tutor-service-....run.app`).
    *   Access this URL in your browser. Perform a hard refresh (Cmd+Shift+R or Ctrl+Shift+R) or use an incognito window, especially after changes.
    *   If you encounter issues, check the Cloud Run logs. You can get the revision name from the deployment output or the Cloud Console.
        ```bash
        gcloud run services logs read ai-tutor-service --region=us-central1 --limit=100 --revision=<NEW_REVISION_NAME>
        ```
        Or, for more detailed structured logging:
        ```bash
        gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ai-tutor-service AND resource.labels.revision_name=<NEW_REVISION_NAME>" --project=<YOUR_PROJECT_ID> --limit=100 --format=json
        ```

---

This guide should help you manage and deploy your AI Tutor application effectively. 