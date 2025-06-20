// Header.tsx

import { useDispatch } from "react-redux"; // создадим ниже
import styled from "./Header.module.css";
import logo from "../../../assets/moto.png";
import { setUser } from "../../../features/auth/authSlice";
import {
  useLoginTelegramMutation,
  type TelegramAuthPayload,
} from "../../../features/auth/authApi";
import TelegramButton from "../TelegramButton/TelegramButton";
import { useAppSelector } from "../../../hook/useAppSelector";
import { ExitButton } from "../ExitButton/ExitButton";

export const Header: React.FC = () => {
  const [loginTelegram, { isLoading }] = useLoginTelegramMutation();
  const { username, first_name, photo_url } = useAppSelector(
    (state) => state.auth
  );

  const dispatch = useDispatch();

  const handleTelegramAuth = async (user: TelegramAuthPayload) => {
    try {
      const {
        id,
        first_name,
        last_name,
        username,
        photo_url,
        auth_date,
        hash,
      } = user;
      const payload = {
        id,
        first_name,
        last_name,
        username,
        photo_url,
        auth_date,
        hash,
      };

      const { access_token } = await loginTelegram(payload).unwrap();
      localStorage.setItem("access_token", access_token);
      dispatch(setUser({ username, first_name, photo_url })); // сохраним юзернейм в store
    } catch (e) {
      console.error("Ошибка авторизации через Telegram:", e);
    }
  };
  return (
    <header className={styled.header}>
      <a href="#">
        <img className={styled.logo__img} src={logo} alt="Логотип" />
      </a>
      <div className={styled.auth}>
        {isLoading && <span></span>}
        {!username ? (
          <TelegramButton
            botName="SimplyMenuBot"
            onAuth={handleTelegramAuth}
            requestAccess="write"
            shouldRender={!username}
          />
        ) : (
          <div className={styled.user_container}>
            <div className={styled.user}>
              {photo_url && (
                <img src={photo_url} alt="avatar" className={styled.avatar} />
              )}
              <span>{first_name || username}</span>
            </div>
            <ExitButton/>
          </div>
        )}
      </div>
    </header>
  );
};
