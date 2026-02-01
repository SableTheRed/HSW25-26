# Inside Out!

# Team Members
Anya Morris  
Harry Taylor  
Emre Acarsoy  
Isobel Ryder  
Alya Ormon  

# Demo video
[Video](demo.mp4)

# Features
- Journaling + sentiment & emotional classification
- Imrproves decisions using historical emotional data
- AI Agents recommends actions, plans, and behavioural adjustments

# Instructions
Navigate into `src` directory.
```
cd src
```
Create virtual environment.
- Windows
  ```
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- Linux
  ```
  python3 -m venv venv
  source venv/scripts/activate
  ```

Install dependencies
```
pip install -r requirements.txt
```

Set environment variables
- Windows
  ```
  $env:OIDC_ISSUER = "https://accounts.google.com"
  $env:OIDC_CLIENT_ID = ""
  $env:OIDC_CLIENT_SECRET = ""
  ```
- Linux
  ```
  export OIDC_ISSUER="https://accounts.google.com"
  export OIDC_CLIENT_ID=""
  export OIDC_CLIENT_SECRET=""
  ```