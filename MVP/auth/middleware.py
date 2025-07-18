import os
import requests
from logger import get_logger

logger = get_logger(__file__)

class AuthMiddleware:
    def __init__(self, redis_manager,
                 BASE_URL, HEALTH_CHECK_URL=None, ACTIVITY_URL=None, VERIFY_AUTH_URL=None, LOGOUT_URL=None):
        self.redis_manager = redis_manager
        self.redirection_url = BASE_URL
        self.health_check_url = HEALTH_CHECK_URL
        self.activity_url = ACTIVITY_URL
        self.verify_token_url = VERIFY_AUTH_URL
        self.logout_url = LOGOUT_URL

    def ready(self, st):
        if self.health_check_url and not self._health_check():
            st.error("Health check failed. Exiting...")
            logger.error("Health check failed. Exiting...")
            st.stop()
        if not self.redis_manager.ready():
            st.error("Redis not ready. Exiting...")
            logger.error("Redis not ready. Exiting...")
            st.stop()
        return True

    def _health_check(self):
        response = requests.get(self.health_check_url, verify=False)
        return response.status_code == 200

    def _verify_token(self, token, response_data=False):
        try:
            response = requests.post(
                self.verify_token_url,
                json={"token": token},
                headers={"Content-Type": "application/json"},
                verify=False
            )
            logger.info(f"verify_token HTTP {response.status_code}: {response.text}")
            if response.status_code == 200:
                if response_data:
                    return True, response.json()
                return True
            else:
                if response_data:
                    return False, response.json()  # or None
                return False
        except Exception as e:
            logger.error(f"verify_token exception: {e}")
            if response_data:
                return False, None
            return False

    def get_user_info(self, session_id=None, st=None, ip="localhost"):
        token = self._retrieve_token(session_id=session_id, st=st)

        logger.info(f"Token used in get_user_info(): {token}")
        logger.info(f"Token used in get_user_info(): {token}")

        if not token:
            logger.warning("Token is None in get_user_info().")
            return None

        try:
            status, response = self._verify_token(token, response_data=True)
            logger.info(f"verify_token returned: status={status}, response={response}")
            if status and response and isinstance(response, dict):
                user_info = response.get('user_info')
                logger.info(f"user_info extracted: {user_info}")
                return user_info
            else:
                logger.warning("verify_token did not return valid user_info")
                return None
        except Exception as e:
            logger.error(f"Exception in get_user_info(): {e}")
            return None

    def authorize(self, force=False, session_id=None, st=None, auth_token=None):
        if force:
            logger.info("Forcing authorization...")
            return True

        if not session_id or not st:
            st.error("Session ID or Streamlit context missing.")
            st.stop()

        if auth_token:
            logger.info("[authorize] Verifying token from query params.")
            status, response = self._verify_token(auth_token, response_data=True)

            if status:
                self._store_token(session_id, st, auth_token, response)
                return True
            else:
                if isinstance(response, dict):
                    error_type = response.get("error", "")
                    message = response.get("message", "Unauthorized access.")
                    if error_type == "Forbidden":
                        logger.warning(f"[authorize] Forbidden access: {message}")
                        st.error(message)
                        st.stop()
                    else:
                        logger.info("[authorize] Invalid or expired token. Skipping further checks.")
                        return False
                else:
                    logger.warning("[authorize] Unexpected response format from token verification.")
                    return False

        logger.info("[authorize] No token in URL. Checking session/Redis.")
        auth_token = self._retrieve_token(session_id, st)
        return self._verify_token(auth_token)

    def _store_token(self, session_id, st, auth_token, response):
        try:
            exp = response.get("user_info", {}).get("exp")

            if session_id:
                st.session_state[session_id] = auth_token
                self.redis_manager.set(session_id, str(auth_token), time=exp)
                logger.info(f"Token stored in Redis for session ID: {session_id}")

            # if ip:
            #     self.redis_manager.set(str(ip), str(auth_token), time=exp)
            #     logger.info(f"Token also stored in Redis for IP: {ip}")

        except Exception as e:
            logger.error(f"Failed to store token: {e}")

    def _retrieve_token(self, session_id, st):
        try:
            if session_id in st.session_state:
                logger.info(f"Token retrieved from session_state for session ID: {session_id}")
                return st.session_state[session_id]

            auth_token = self.redis_manager.get(session_id)
            if auth_token:
                logger.info(f"Token retrieved from Redis for session ID: {session_id} => {auth_token}")
                st.session_state[session_id] = auth_token
                return auth_token
            else:
                logger.warning(f"No token found in Redis for session ID: {session_id}")

            # # Fallback to IP
            # auth_token = self.redis_manager.get(str(ip))
            # if auth_token:
            #     logger.info(f"Token retrieved from Redis for IP: {ip} => {auth_token}")
            #     return auth_token
            # else:
            #     logger.warning(f"No token found in Redis for IP: {ip}")
            #     return None

        except Exception as e:
            logger.error(f"Failed to retrieve token: {e}")
            return None

    def deauthorize(self, st, logger, ip, message, type, session_id):
        auth_token = self._retrieve_token(session_id, st, ip)
        logger.info("Logging out...")  # Only log in JSON logger
        logout_url = f"{self.logout_url}?redirectUrl={self.redirection_url}"
        logout_url += f"&auth_token={auth_token}"
        if session_id:
            self.redis_manager.delete(str(session_id))
        else:
            self.redis_manager.delete(str(ip))
        st.markdown(f"<meta http-equiv='refresh' content='0;url={logout_url}'>", unsafe_allow_html=True)
