@echo off
FOR /F "delims=" %%i IN ('"C:\Users\User\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" components copy-bundled-python') DO SET CLOUDSDK_PYTHON=%%i
echo Installing kubectl and gke-gcloud-auth-plugin...
"C:\Users\User\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" components install kubectl gke-gcloud-auth-plugin --quiet
echo DONE
