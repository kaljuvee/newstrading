from twilio.rest import Client

account_sid = 'AC34a68f2862daadd1b07547cfabf0dc10'
auth_token = '21f888994d57768bb4a7f70cb8e3b6b8'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  to='whatsapp:+447585099329'
)

print(message.sid)