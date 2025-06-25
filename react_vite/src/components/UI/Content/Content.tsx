import React from "react";
import styled from "./Content.module.css";
import { Button } from "../Button/Button";
import { Link } from "react-router";
import { SOSButton } from "../SOSButton/SOSButton";
import { useAppSelector } from "../../../hook/useAppSelector";

export const Content: React.FC = () => {
  const { username } = useAppSelector((state) => state.auth);
  
  return (
    <>
      <ul className={styled.content}>
        <li>
          <a
            href="https://t.me/iwmcc64"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="white" fontSize={20}>
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
            <Button variant="white" fontSize={20}>
              Наш телеграмм канал
            </Button>
          </a>
        </li>

        {/*<li><Link to={'/servisec'}><Button variant="white" fontSize={20}>Услуги</Button></Link></li>
           <li><Link to={'/sales'}><Button variant="white" fontSize={20}>Объявления</Button></Link></li>*/}
        <li>
          {username && (
            <Link to={"/sos"}>
            <SOSButton />
          </Link>
          )}
          
        </li>
      </ul>
    </>
  );
};
