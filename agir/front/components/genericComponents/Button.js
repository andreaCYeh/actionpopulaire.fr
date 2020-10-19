import style from "./style.scss";
import styled from "styled-components";
import PropTypes from "prop-types";
import { transparentize } from "polished";
import { icons } from "feather-icons";

const buttonColors = {
  default: {
    background: style.black50,
    hoverBackground: style.black100,
    labelColor: style.black1000,
  },
  primary: {
    background: style.primary500,
    labelColor: style.white,
    hoverBackground: style.primary600,
  },
  secondary: {
    background: style.secondary500,
    labelColor: style.white,
    hoverBackground: style.secondary600,
  },
  confirmed: {
    background: style.primary100,
    hoverBackground: style.primary150,
    labelColor: style.primary500,
  },
  unavailable: {
    background: style.white,
    hoverBackground: style.white,
    labelColor: style.black500,
    borderColor: style.black100,
  },
};

const Button = styled.button.attrs(({ color }) => buttonColors[color])`
  display: inline-block;
  padding: ${({ small }) => (small ? "0.5rem 0.75rem" : "0.75rem 1.5rem")};
  line-height: ${({ small }) =>
    small
      ? "95%"
      : "1.5rem"}; /* pour s'assurer que les liens sont correctement centrés */
  margin: 0;
  border-radius: 0.5rem;
  min-height: ${({ small }) => (small ? "2rem" : "3rem")};
  text-align: center;
  text-transform: uppercase;
  font-weight: 700;
  font-size: ${({ small }) => (small ? "0.6875rem" : "0.875rem")};

  color: ${({ labelColor, disabled }) =>
    disabled ? transparentize(0.3, labelColor) : labelColor};
  background-color: ${({ background, disabled }) =>
    disabled ? transparentize(0.7, background) : background};
  border: ${({ borderColor }) =>
    borderColor ? `1px solid ${borderColor}` : "0"};

  &:hover {
    background-color: ${({ hoverBackground }) => hoverBackground};
    text-decoration: none;
  }
  
  ${({ disabled }) => disabled && "cursor: not-allowed;"}

  ${({ icon, small }) =>
    icon
      ? `
    &:before {
      content: url('data:image/svg+xml;utf8,${icons[icon].toSvg({
        height: small ? 11 : 16,
        width: small ? 11 : 16,
      })}');
      position: relative;
      top: 0.15rem;
      margin-right: ${small ? "0.25rem" : "0.5rem"};
    }
  `
      : ""}
}}
`;

Button.colors = Object.keys(buttonColors);

Button.propTypes = {
  onClick: PropTypes.func,
  color: PropTypes.oneOf(Button.colors),
  small: PropTypes.bool,
  disabled: PropTypes.bool,
  href: PropTypes.string,
  block: PropTypes.bool,
};

Button.defaultProps = {
  color: "default",
  small: false,
  block: false,
};

export default Button;
