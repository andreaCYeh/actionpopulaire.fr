import PropTypes from "prop-types";
import React, { useCallback, useMemo, useRef, useState } from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import { Column, Row } from "@agir/front/genericComponents/grid";

import facebookLogo from "@agir/front/genericComponents/logos/facebook.svg";
import twitterLogo from "@agir/front/genericComponents/logos/twitter.svg";
import telegramLogo from "@agir/front/genericComponents/logos/telegram.svg";
import whatsappLogo from "@agir/front/genericComponents/logos/whatsapp.svg";
import styled from "styled-components";

let logoSpacing = { margin: "0 8px" };

const StyledCard = styled(Card)`
  margin-bottom: 24px;
  overflow: hidden;
  border-bottom: 1px solid ${style.black50};
`;

const ShareCard = (props) => {
  const { url, title } = props;

  const encodedLocation = useMemo(() => {
    return url
      ? encodeURIComponent(url)
      : encodeURIComponent(window.location.href);
  }, [url]);

  let [copied, setCopied] = useState(false);
  let copyUrl = useCallback(() => {
    inputEl.current.select();
    document.execCommand("copy");
    setCopied(true);
  }, []);

  const inputEl = useRef(null);
  return (
    <StyledCard style={{ padding: "1.5rem" }}>
      <Row gutter={2} style={{ marginBottom: "1rem" }}>
        <Column grow collapse={false}>
          <b>{title || "Partager"}</b>
        </Column>
        <Column collapse={false}>
          <a
            href={`https://wa.me/?text=${encodedLocation}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              src={whatsappLogo}
              width="24"
              height="25"
              style={logoSpacing}
              alt="Whatsapp"
            />
          </a>
          <a
            href={`https://t.me/share/url?url=${encodedLocation}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              src={telegramLogo}
              width="24"
              height="24"
              style={logoSpacing}
              alt="Telegram"
            />
          </a>
          <a
            href={`https://www.facebook.com/sharer/sharer.php?u=${encodedLocation}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              src={facebookLogo}
              width="24"
              height="24"
              style={logoSpacing}
              alt="Facebook"
            />
          </a>
          <a
            href={`https://twitter.com/intent/tweet?text=${encodedLocation}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              src={twitterLogo}
              width="24"
              height="20"
              style={{ ...logoSpacing, marginRight: 0 }}
              alt="Twitter"
            />
          </a>
        </Column>
      </Row>

      <Row gutter={4}>
        <Column grow collapse={false}>
          {" "}
          <input
            type="text"
            value={window.location.href}
            style={{
              width: "100%",
              height: "32px",
              border: `1px solid ${style.black100}`,
              borderRadius: style.softBorderRadius,
              padding: "8px",
            }}
            readOnly
            ref={inputEl}
            onClick={copyUrl}
          />
        </Column>
        <Column collapse={false}>
          <Button small icon={copied ? "check" : "copy"} onClick={copyUrl}>
            Copier le lien
          </Button>
        </Column>
      </Row>
    </StyledCard>
  );
};
ShareCard.propTypes = {
  title: PropTypes.string,
  url: PropTypes.string,
};
export default ShareCard;
