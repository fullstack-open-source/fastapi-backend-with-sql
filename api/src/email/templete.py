ONETIME_VERIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Verification Code</title>
    <style>
        body {{
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 15px;
            background-color: #f9f9f9;
        }}
        a {{
            color: #7F4975;
            text-decoration: none;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        table {{
            display: none;
        }}
    </style>
</head>
<body>
    <div style="max-width: 680px; margin: 0 auto; padding: 45px 30px 60px; background: #f4f7ff; background-image: url(https://storage.googleapis.com/klikyai-bucket/style-generation-thumbnail-url/faceswap_1725541603948_kFM8SaMfmFaQRjYAqUVt.png); background-repeat: no-repeat; background-size: 800px 452px; background-position: top center; font-size: 14px; color: #291835;">

        <div style="margin: 0; margin-top: 70px; padding: 60px 30px 60px; background: #FFFFFF; border-radius: 30px; text-align: center;">
            <div style="width: 100%;">
                <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #1f1f1f;">
                    Your Verification Code
                </h1>

                <p style="margin: 0; margin-top: 20px; font-size: 16px; font-weight: 500;">
                    Use the code below to complete your action.
                </p>

                <div style="margin-top: 30px;">
                    <div style="display: inline-block; padding: 20px 40px; background-color: #22bb33; color: white; font-size: 28px; font-weight: bold; border-radius: 10px; letter-spacing: 6px;">
                        {code}
                    </div>
                </div>

                <p style="margin: 0; margin-top: 25px; font-size: 14px; color: #555;">
                    This code is valid for 10 minutes. If you didn’t request this, you can safely ignore this email.
                </p>
            </div>
        </div>

        <p style="max-width: 400px; margin: 0 auto; margin-top: 90px; text-align: center; font-weight: 500; color: #8c8c8c;">
            Need help? Ask at <a href="mailto:info@klikyai.com" style="color: #499fb6;">info@klikyai.com</a>
            or visit our <a href="#" target="_blank" style="color: #499fb6;">Help Center</a>
        </p>

        <footer style="width: 100%; max-width: 490px; margin: 20px auto 0; text-align: center; border-top: 1px solid #e6ebf1;">
            <p style="margin: 0; margin-top: 16px; color: #291835;">Copyright © 2024 Kliky AI Screen. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
"""
