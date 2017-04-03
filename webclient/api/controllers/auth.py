import traceback
from bson import json_util
from flask_restful import Resource, abort, reqparse
from flask import Response
from webclient.api.models.users import validate_user, create_user


class Login(Resource):
    """
    Resource representing '/api/v1.0/auth/login/' api route

    available methods: POST
    """
    @classmethod
    def post(cls):
        """
        Logins user

        POST /api/v1.0/auth/login/

        Request body parameters:
            :email: login email
            :password: login password

        :return: JSON web token
        """
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Login email address', required=True)
        parser.add_argument('password', type=str, help='Login password', required=True)

        args = parser.parse_args()

        email = args.get('email')
        password = args.get('password')

        try:
            token = validate_user(email, password)
            return {'token': token}
        except Exception as error:
            traceback.print_exc()
            abort(400, message='Error while loging in: %s' % str(error))


class Register(Resource):
    """
    Resource representing '/api/v1.0/auth/register/' api route

    available methods: POST
    """
    @classmethod
    def post(cls):
        """
        Creates user

        POST /api/v1.0/auth/register/

        Request body parameters:
            :name: user name
            :email: user email address
            :password: user password
            :password_confirm: password confirmation

        :return: Newly created user ID
        """
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, help='User name', required=True)
        parser.add_argument('email', type=str, help='User email address', required=True)
        parser.add_argument('password', type=str, help='User password', required=True)
        parser.add_argument('password_confirm', type=str, help='Password confirmation', required=True)

        args = parser.parse_args()

        email = args.get('email')
        password = args.get('password')
        password_confirm = args.get('password_confirm')
        name = args.get('name')

        user_id = None
        try:
            user_id = create_user(name, email, password, password_confirm)
        except Exception as error:
            traceback.print_exc()
            abort(400, message='Error while creating account: %s' % str(error))

        response = Response(json_util.dumps({'user': user_id}), mimetype='application/json')
        return response
