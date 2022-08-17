import ElasticEmail
from ElasticEmail.api import emails_api
from ElasticEmail.model.email_message_data import EmailMessageData
from ElasticEmail.model.email_recipient import EmailRecipient


configuration = ElasticEmail.Configuration(
    host="https://api.elasticemail.com/v4"
)
configuration.api_key['apikey'] = '8611CF97BFA3173A5CD6E9D02C16ADF6A5DFC02097F6DB0E82B221F6CE1CC3D9F11FA3E3CF54EF707CA6F01AE10955CF'


def email_verify_send(email_address, code):
    with ElasticEmail.ApiClient(configuration) as api_client:
        api_instance = emails_api.EmailsApi(api_client)
        email_message_data = EmailMessageData(
            recipients=[
                EmailRecipient(
                    email=email_address
                ),
            ],
            content={
                "Body": [
                    {
                        "ContentType": "HTML",
                        "Content": "<h3>테스트회사 회원가입 이메일 인증</h3>"
                        + "이메일 인증코드는 " + code + " 입니다.<br><br>"
                        + "인증코드는 3시간 동안만 유효합니다.<br>감사합니다."
                    }
                ],
                "Subject": "테스트회사 회원가입 이메일 인증 코드입니다.",
                "From": "테스트회사 <no-reply@abz.kr>"
            }
        )

        try:
            api_instance.emails_post(email_message_data)
        except ElasticEmail.ApiException as e:
            print("Exception when calling EmailsApi: %s\n" % e)


def email_find_account_send(email_address, member_id, hash_url):
    with ElasticEmail.ApiClient(configuration) as api_client:
        api_instance = emails_api.EmailsApi(api_client)
        email_message_data = EmailMessageData(
            recipients=[
                EmailRecipient(
                    email=email_address
                ),
            ],
            content={
                "Body": [
                    {
                        "ContentType": "HTML",
                        "Content": '<h3>테스트회사 비밀번호 변경 링크</h3>'
                        + '비밀번호를 바꿀 회원님의 아이디: ' + member_id + '<br><br>'
                        + '아래 링크를 클릭하여, 비밀번호를 변경해주세요. <br>'
                        + '<a href="' + hash_url + '" >' + hash_url + '</a><br><br>'
                        + '링크는 3시간 동안만 유효합니다.<br>감사합니다.'
                    }
                ],
                "Subject": member_id + "님, 비밀번호 변경 링크 드립니다. 즉시 확인해주세요.",
                "From": "테스트회사 <no-reply@abz.kr>"
            }
        )

        try:
            api_instance.emails_post(email_message_data)
        except ElasticEmail.ApiException as e:
            print("Exception when calling EmailsApi: %s\n" % e)