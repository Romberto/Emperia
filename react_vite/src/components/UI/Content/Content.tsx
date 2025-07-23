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
    <>
      <ul className={styled.content}>
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

        {/*<li><Link to={'/servisec'}><Button variant="white" fontSize={20}>Услуги</Button></Link></li>
           <li><Link to={'/sales'}><Button variant="white" fontSize={20}>Объявления</Button></Link></li>*/}
        <li>
          {access_token && (
            <a href="#" onClick={() => dispatch(setSosModulOpen())}>
              <SOSButton />
            </a>
          )}
        </li>
      </ul>
    </>
  );
};
