## EC2 Setup Commands for Running FastAPI App
sudo apt update
sudo apt install -y python3-pip python3-venv

mkdir -p ~/mortgage-risk-fastapi
cd ~/mortgage-risk-fastapi

python3 -m venv .venv
source .venv/bin/activate

mkdir -p app
pip install fastapi uvicorn pandas pyarrow s3fs boto3
### Running the FastAPI app manually for testing before background service setup
uvicorn app.fastapiApp :app --host 0.0.0.0 --port 8000

### Creating the systemd service file so FastAPI can run in the background
sudo nano /etc/systemd/system/mortgage-risk-fastapi.service

### Reloading systemd so it detects the new service file
### Enabling the service so it can start automatically
### Checking whether the FastAPI service is running properly
### Starting the FastAPI service
sudo systemctl daemon-reload
sudo systemctl enable mortgage-risk-fastapi
sudo systemctl start mortgage-risk-fastapi
sudo systemctl status mortgage-risk-fastapi


## Testing in browser

Once the FastAPI service is running, open the app using the EC2 public DNS name on port `8000`.

Examples :
- `http://<EC2-PUBLIC-DNS> :8000/`
- `http://<EC2-PUBLIC-DNS> :8000/health`
- `http://<EC2-PUBLIC-DNS> :8000/docs`

Example pattern :
- `http://ec2-xx-xxx-xxx-xxx.compute-1.amazonaws.com :8000/health`

Notes :
- The security group must allow inbound traffic on port `8000` from the allowed IP.
- This setup uses `http`, not `https`.
- Swagger UI is available at `/docs`.
