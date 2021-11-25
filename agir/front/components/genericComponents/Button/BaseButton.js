import PropTypes from "prop-types";
import React from "react";
import styled, { keyframes } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";

import { ICONS, getIconDataUrl } from "./utils";

const spinner = keyframes`
  0% {
    transform: rotate(0turn);
    stroke-dashoffset: 0.662em;
  }
  50% {
    transform: rotate(2turn);
    stroke-dashoffset: 3.138em;
  }
  100% {
    transform: rotate(3turn);
    stroke-dashoffset: 0.662em;
  }
`;

export const ButtonLoader = styled.i
  .withConfig({
    shouldForwardProp: (prop) => ["loading", "theme"].includes(prop) === false,
  })
  .attrs((attrs) => ({
    ...attrs,
    children: (
      <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
        <circle cx="8" cy="8" r="7" />
      </svg>
    ),
  }))`
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  padding: 0;
  margin: 0;
  background-color: inherit;
  z-index: ${({ loading }) => (loading ? 1 : -1)};

  & > svg {
    opacity: ${({ loading }) => (loading ? 1 : 0)};
    transition: opacity, width, height 150ms ease-in-out;
    width: ${({ loading }) => (loading ? 1 : 0)}em;
    height: ${({ loading }) => (loading ? 1 : 0)}em;

    circle {
        fill: transparent;
        stroke: currentColor;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-dasharray: 3.138em;
        transform-origin: center center;
        animation-name: ${({ loading }) => (loading ? spinner : "none")};
        animation-iteration-count: infinite;
        animation-easing-function: linear;
        animation-direction: forwards;
        animation-duration: 3s;
    }
  }

  & + span {
    transition: opacity 250ms ease-in-out;
    opacity: ${({ loading }) => (loading ? 0 : 1)};
  }
`;

export const BaseButton = styled.button
  .withConfig({
    shouldForwardProp: (prop) =>
      ["loading", "link", "small", "block", "wrap"].includes(prop) === false,
  })
  .attrs(({ link, as, loading, children, ...rest }) => ({
    ...rest,
    as: link ? Link : as,
    children: (
      <>
        <ButtonLoader loading={loading} />
        <span>{children}</span>
      </>
    ),
  }))`
  margin: 0;
  justify-content: center;
  align-items: center;
  text-align: center;
  font-weight: 500;
  border: 1px solid;
  cursor: pointer;
  position: relative;

  white-space: ${({ wrap }) => (wrap ? "normal" : "nowrap")};
  text-overflow: ${({ wrap }) => (wrap ? "inherit" : "ellipsis")};
  overflow: ${({ wrap }) => (wrap ? "auto" : "hidden")};

  display: ${({ block }) => (block ? "flex" : "inline-flex")};
  width: ${({ block }) => (block ? "100%" : "auto")};

  padding: ${({ small }) => (small ? "0.5rem 0.75rem" : "0.75rem 1.5rem")};
  line-height: ${({ small }) => (small ? "1" : "1.5")};
  font-size: ${({ small }) => (small ? "0.875rem" : "1rem")};

  border-radius: ${style.borderRadius};

  background-color: ${style.black50};
  border-color: ${style.black50};
  color: ${style.black1000};

  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    cursor: not-allowed;
  }

  &:before {
    flex: 0 0 auto;
    background-image: ${getIconDataUrl({ color: style.black1000 })};
    content: "";
    height: 1rem;
    width: 1rem;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center center;
    margin-right: ${({ small }) => (small ? "0.375rem" : "0.5rem")};
    display: ${({ icon }) => (icon && ICONS[icon] ? "inline-block" : "none")};
  }

  & > * {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    & > * {
      flex: 0 0 auto;
    }
  }
}}
`;

BaseButton.propTypes = {
  link: PropTypes.bool,
  disabled: PropTypes.bool,
  small: PropTypes.bool,
  block: PropTypes.bool,
  wrap: PropTypes.bool,
  loading: PropTypes.bool,
  icon: PropTypes.string,
};
BaseButton.defaultProps = {
  link: false,
  disabled: false,
  small: false,
  block: false,
  wrap: false,
  loading: false,
};

export default BaseButton;
