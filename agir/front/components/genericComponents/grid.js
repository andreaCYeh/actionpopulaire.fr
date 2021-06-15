import styled from "styled-components";
import PropTypes from "prop-types";
import Card from "./Card";
import style from "@agir/front/genericComponents/_variables.scss";
import { useCallback, useEffect, useMemo, useState } from "react";
import React from "react";

/**
 * Accessibility
 */

export const SROnly = styled.span`
  border: 0 !important;
  clip: rect(1px, 1px, 1px, 1px) !important;
  -webkit-clip-path: inset(50%) !important;
  clip-path: inset(50%) !important;
  height: 1px !important;
  overflow: hidden !important;
  padding: 0 !important;
  position: absolute !important;
  width: 1px !important;
  white-space: nowrap !important;
`;

/**
 * Text
 */
export const Center = styled.div`
  text-align: center;
`;

export const Right = styled.div`
  text-align: right;
`;

export const PullRight = styled.div`
  float: right;
`;

/**
 * Media queries
 */
export const Hide = styled.div`
  min-width: 0;

  @media (max-width: ${({ under }) => (under === true ? collapse : under)}px) {
    display: none;
  }

  @media (min-width: ${({ over }) => (over === true ? collapse : over)}px) {
    display: none;
  }
`;

/**
 * Grid
 */

const gutter = 16;
const collapse = style.collapse;

export const GrayBackground = styled.div`
  background-color: ${style.black25};
`;

export const Column = styled.div`
  flex-basis: ${({ width, grow }) =>
    width || grow
      ? (Array.isArray(width) && width[1] ? width[1] : width) || "1px"
      : "auto"};
  flex-grow: ${({ grow }) => (grow ? 1 : 0)};
  & > ${Card} {
    margin-bottom: 16px;
  }

  @media (max-width: ${(props) =>
      typeof props.collapse === "undefined"
        ? collapse
        : props.collapse || 0}px) {
    flex-basis: ${(props) =>
      Array.isArray(props.width) && props.width[0] ? props.width[0] : "100%"};
    padding-left: 0;
    padding-right: 0;

    & > ${Column} > ${Card} {
      ${(props) => (props.stack ? "margin-bottom: 0px;" : "")}
    }
  }
`;

Column.propTypes = {
  width: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string),
  ]), // can be anything like "50%" "400px"
  // if array first is mobile size, second is desktop
  grow: PropTypes.bool, // does the column fill the remaining space
};

export const Row = styled.div`
  margin-left: -${(props) => (typeof props.gutter === "undefined" ? gutter : props.gutter)}px;
  margin-right: -${(props) => (typeof props.gutter === "undefined" ? gutter : props.gutter)}px;
  display: flex;
  flex-wrap: wrap;
  align-items: ${({ align }) => align || "stretch"};
  justify-content: ${({ justify }) => justify || "start"};

  & > ${Column} {
    padding-left: ${(props) =>
      typeof props.gutter === "undefined" ? gutter : props.gutter}px;
    padding-right: ${(props) =>
      typeof props.gutter === "undefined" ? gutter : props.gutter}px;
  }

  & > ${Column} > section {
    margin-left: -${(props) => (typeof props.gutter === "undefined" ? gutter : props.gutter)}px;
    margin-right: -${(props) => (typeof props.gutter === "undefined" ? gutter : props.gutter)}px;
    border-radius: 0px;
  }

  @media (max-width: ${(props) =>
      typeof props.collapse === "undefined"
        ? collapse
        : props.collapse || 0}px) {
    & > ${Column} > ${Card} {
      margin-left: -${(props) => (typeof props.gutter === "undefined" ? gutter : props.gutter)}px;
      margin-right: -${(props) => (typeof props.gutter === "undefined" ? gutter : props.gutter)}px;
      border-radius: 0px;
    }
  }
`;

Row.propTypes = {
  children: PropTypes.node,
  align: PropTypes.oneOf([
    "stretch",
    "baseline",
    "center",
    "flex-start",
    "flex-end",
  ]), // align-items CSS property
  justify: PropTypes.oneOf([
    "flex-start",
    "flex-end",
    "center",
    "space-between",
    "space-around",
    "space-evenly",
  ]), // justify-content CSS property
};

export const Container = styled.section`
  width: ${1400 + gutter * 2}px;
  max-width: 100%;
  margin: 0 auto;
  padding-left: ${gutter}px;
  padding-right: ${gutter}px;

  & > ${Row} {
    margin-left: -${gutter}px;
    margin-right: -${gutter}px;
  }
`;

export const useIsDesktop = (breakpoint) => {
  breakpoint = breakpoint || collapse;
  const [isDesktop, setDesktop] = useState(window.innerWidth > breakpoint);

  let refresh = useCallback(
    () => setDesktop(window.innerWidth > breakpoint),
    [breakpoint]
  );

  useEffect(() => {
    window.addEventListener("resize", refresh);

    return function cleanup() {
      window.removeEventListener("resize", refresh);
    };
  }, [refresh]);

  return isDesktop;
};

export const ResponsiveLayout = ({
  MobileLayout,
  DesktopLayout,
  breakpoint,
  ...props
}) => {
  const isDesktop = useIsDesktop(breakpoint);

  return isDesktop ? <DesktopLayout {...props} /> : <MobileLayout {...props} />;
};
ResponsiveLayout.propTypes = {
  MobileLayout: PropTypes.oneOfType([PropTypes.element, PropTypes.func])
    .isRequired,
  DesktopLayout: PropTypes.oneOfType([PropTypes.element, PropTypes.func])
    .isRequired,
  breakpoint: PropTypes.number,
};

export const useResponsiveMemo = (mobileValue, desktopValue, breakpoint) => {
  const isDesktop = useIsDesktop(breakpoint);

  const value = useMemo(
    () => (isDesktop ? desktopValue : mobileValue),
    [isDesktop, mobileValue, desktopValue]
  );

  return value;
};
