# subscriptions/paypal_service.py
import requests
import base64
import json
from django.conf import settings

class PayPalService:
    @staticmethod
    def get_access_token():
        """Get PayPal access token with better error handling"""
        try:
            print("🔑 Getting PayPal access token...")
            print(f"Client ID: {settings.PAYPAL_CLIENT_ID[:10]}...")
            print(f"Mode: {settings.PAYPAL_MODE}")
            print(f"Secret: {settings.PAYPAL_CLIENT_SECRET[:10]}...")

            # Encode credentials
            auth_string = f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            # Determine API endpoint
            if settings.PAYPAL_MODE == "sandbox":
                base_url = "https://api.sandbox.paypal.com"
            else:
                base_url = "https://api.paypal.com"
            
            # Request access token
            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {"grant_type": "client_credentials"}
            
            print(f"🌐 Sending request to: {base_url}/v1/oauth2/token")
            
            response = requests.post(
                f"{base_url}/v1/oauth2/token",
                headers=headers,
                data=data,
                timeout=30
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print("✅ Access token received successfully")
                return token_data["access_token"]
            else:
                error_detail = response.text
                print(f"❌ PayPal auth failed: {response.status_code} - {error_detail}")
                
                # More specific error messages
                if "invalid_client" in error_detail:
                    raise Exception("Invalid PayPal credentials. Please check your Client ID and Secret.")
                elif "unauthorized" in error_detail.lower():
                    raise Exception("Unauthorized access. Check if your sandbox account is active.")
                else:
                    raise Exception(f"PayPal authentication failed: {error_detail}")
                
        except requests.exceptions.RequestException as e:
            print(f"🌐 Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            print(f"💥 Unexpected error: {str(e)}")
            raise Exception(f"Failed to get access token: {str(e)}")
    
    @staticmethod
    def create_payment(plan_id, user_id, return_url, cancel_url):
        """Create PayPal payment using direct API"""
        from .models import SubscriptionPlan
        
        try:
            print("💰 Creating PayPal payment...")
            plan = SubscriptionPlan.objects.get(id=plan_id)
            print(f"📦 Plan: {plan.name} - ₱{plan.price}")
            
            access_token = PayPalService.get_access_token()
            
            # Determine API endpoint
            if settings.PAYPAL_MODE == "sandbox":
                base_url = "https://api.sandbox.paypal.com"
            else:
                base_url = "https://api.paypal.com"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "PHP",
                        "value": str(float(plan.price))
                    },
                    "description": f"FileGuard {plan.name} Subscription"
                }],
                "application_context": {
                    "brand_name": "FileGuard",
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW",
                    "return_url": return_url,
                    "cancel_url": cancel_url
                }
            }
            
            print(f"🌐 Creating payment at: {base_url}/v2/checkout/orders")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{base_url}/v2/checkout/orders",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"📡 Payment creation response: {response.status_code}")
            
            if response.status_code == 201:
                payment_data = response.json()
                print(f"✅ Payment created: {payment_data['id']}")
                print(f"🔗 Status: {payment_data['status']}")
                
                # Find approval URL
                approval_link = next(
                    link for link in payment_data["links"] 
                    if link["rel"] == "approve"
                )
                
                return {
                    'id': payment_data['id'],
                    'status': payment_data['status'],
                    'approval_url': approval_link['href']
                }
            else:
                error_detail = response.text
                print(f"❌ Payment creation failed: {response.status_code} - {error_detail}")
                raise Exception(f"Payment creation failed: {error_detail}")
                
        except Exception as e:
            print(f"💥 Error in create_payment: {str(e)}")
            raise Exception(f"Failed to create payment: {str(e)}")
    
    @staticmethod
    def execute_payment(order_id):
        """Execute payment using direct API (v2)"""
        try:
            print(f"🔄 Executing payment for order: {order_id}")
            access_token = PayPalService.get_access_token()
            
            if settings.PAYPAL_MODE == "sandbox":
                base_url = "https://api.sandbox.paypal.com"
            else:
                base_url = "https://api.paypal.com"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            print(f"🌐 Capturing payment at: {base_url}/v2/checkout/orders/{order_id}/capture")
            
            response = requests.post(
                f"{base_url}/v2/checkout/orders/{order_id}/capture",
                headers=headers,
                json={},
                timeout=30
            )
            
            print(f"📡 Payment execution response: {response.status_code}")
            
            if response.status_code == 201:
                payment_data = response.json()
                print("✅ Payment executed successfully")
                print(f"💰 Status: {payment_data['status']}")
                return payment_data
            else:
                error_detail = response.text
                print(f"❌ Payment execution failed: {response.status_code} - {error_detail}")
                raise Exception(f"Payment execution failed: {error_detail}")
                
        except Exception as e:
            print(f"💥 Error in execute_payment: {str(e)}")
            raise Exception(f"Failed to execute payment: {str(e)}")