import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { NavLink } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { Hide } from "@agir/front/genericComponents/grid";

import BackButton from "./BackButton";

const StyledMenuItem = styled(NavLink)`
  display: flex;
  width: 100%;
  flex-flow: row nowrap;
  align-items: center;
  background-color: transparent;
  text-align: left;
  border: none;
  margin: 0;
  padding: 0;
  font-size: 1rem;
  line-height: 1.1;
  font-weight: 500;
  color: ${({ disabled }) => (disabled ? style.black500 : style.black1000)};
  cursor: ${({ disabled }) => (disabled ? "default" : "pointer")};

  &:hover {
    text-decoration: none;
    cursor: pointer;
  }

  & > * {
    margin: 0;
    padding: 0;
  }

  span {
    flex: 1 1 auto;
  }

  small {
    font-size: 0.75rem;
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: ${({ disabled, active }) => {
      if (disabled) return style.black100;
      if (active) return style.primary500;
      return style.secondary500;
    }};
    color: ${({ disabled, active }) => {
      if (disabled) return style.black500;
      if (active) return "#fff";
      return style.black1000;
    }};
    margin-right: 1rem;
    clip-path: circle(1rem);
    text-align: center;
  }

  &.active {
    span {
      color: ${style.primary500};
    }

    ${RawFeatherIcon} {
      background-color: ${({ disabled }) => {
        if (disabled) return style.black100;
        return style.primary500;
      }};
      color: ${({ disabled }) => {
        if (disabled) return style.black500;
        return style.white;
      }};
    }
  }
`;

const StyledMenu = styled.div`
  width: 100%;
  height: 100%;
  padding: 1.5rem;
  background-color: ${style.black25};
  box-shadow: inset -1px 0px 0px #dfdfdf;

  @media (min-width: ${style.collapse}px) {
    width: 360px;
  }

  h4 {
    font-weight: 700;
    font-size: 1.25rem;
    line-height: 1.51;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      padding: 0.5rem 0;
    }

    hr {
      border-color: ${style.black200};
      margin: 0.5rem 0;
    }
  }
`;

const ManagementMenuItem = (props) => {
  const { object, item } = props;

  const disabled = useMemo(
    () =>
      typeof item.disabled === "function"
        ? item.disabled(object)
        : !!item.disabled,
    [object, item]
  );

  return (
    <StyledMenuItem disabled={disabled} to={item.getLink()}>
      <RawFeatherIcon width="1rem" height="1rem" name={item.icon} />
      <span>
        {item.label}
        <br />
        {disabled && item.disabledLabel && <small>{item.disabledLabel}</small>}
      </span>
    </StyledMenuItem>
  );
};

ManagementMenuItem.propTypes = {
  object: PropTypes.object,
  item: PropTypes.shape({
    id: PropTypes.string,
    label: PropTypes.oneOfType([PropTypes.func, PropTypes.string]),
    disabledLabel: PropTypes.string,
    icon: PropTypes.string,
    disabled: PropTypes.oneOfType([PropTypes.func, PropTypes.bool]),
    getLink: PropTypes.func.isRequired,
    menuGroup: PropTypes.oneOf([1, 2]),
  }),
};

const ManagementMenu = (props) => {
  const { object, items, title, onBack } = props;

  return (
    <StyledMenu>
      <Hide over>
        <BackButton onClick={onBack} />
      </Hide>
      <h4>{title}</h4>
      <ul>
        {items
          .filter((item) => item.menuGroup === 1)
          .map((item) => (
            <li key={item.id}>
              <ManagementMenuItem object={object} item={item} />
            </li>
          ))}
        <hr />
        {items
          .filter((item) => item.menuGroup === 2)
          .map((item) => (
            <li key={item.id}>
              <ManagementMenuItem object={object} item={item} />
            </li>
          ))}
      </ul>
    </StyledMenu>
  );
};
ManagementMenu.propTypes = {
  title: PropTypes.string.isRequired,
  object: PropTypes.object.isRequired,
  items: PropTypes.arrayOf(ManagementMenuItem.propTypes.item).isRequired,
  onBack: PropTypes.func.isRequired,
};

export default ManagementMenu;
