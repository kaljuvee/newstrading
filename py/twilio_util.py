from twilio.rest import Client

account_sid = 'key'
auth_token = 'token'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  to='whatsapp:+447585099329'
)

print(message.sid)
