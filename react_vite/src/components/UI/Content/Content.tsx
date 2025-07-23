import React from "react";
import styled from "./Content.module.css";
import { Button } from "../Button/Button";
import { SOSButton } from "../SOSButton/SOSButton";
import { useAppSelector } from "../../../hook/useAppSelector";
import { useAppDispatch } from "../../../hook/useAppDispatch";
import { setSosModulOpen } from "../../../features/moduls/modulsSlise";

export const Content: React.FC = () => {
  const dispatch = useAppDispatch();
  const { access_token } = useAppSelector((state) => state.auth);

  return (
    <div className={styled.content}>
      {access_token && (
        <ul className={styled.content_list}>
          
          <li>
            <a
              href="https://t.me/iwmcc64"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="black" fontSize={30}>
                Чат (болталка)
              </Button>
            </a>
          </li>
          <li>
            <a
              href="https://t.me/promoto64"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="black" fontSize={30}>
                Наш телеграмм канал
              </Button>
            </a>
          </li>
          <li>
            <a href="#" onClick={() => dispatch(setSosModulOpen())}>
              <SOSButton />
            </a>
          </li>
        </ul>
      )}
    </div>
  );
};
