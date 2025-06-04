import React from "react";
import styled from "./Content.module.css";
import { Button } from "../Button/Button";
import { Link } from "react-router";

export const Content: React.FC = () => {
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
          <Link to={"/sos"}>
            <Button variant="red" fontSize={60}>
              SOS
            </Button>
          </Link>
        </li>
      </ul>
    </>
  );
};
