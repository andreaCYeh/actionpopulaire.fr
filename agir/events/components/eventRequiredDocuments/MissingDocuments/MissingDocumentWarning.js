import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { displayShortDate } from "@agir/lib/utils/time";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledWarning = styled.div`
  padding: 1rem;
  margin: 0 0 2rem;
  background-color: ${(props) => props.theme.white};
  border-radius: ${(props) => props.theme.borderRadius};
  border: 1px solid ${(props) => props.theme.redNSP};
  box-shadow: 0px 0px 2px rgba(233, 58, 85, 0.5),
    0px 3px 3px rgba(233, 58, 85, 0.1);

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0 0 1.5rem;
  }

  & > * {
    width: 100%;
    text-align: left;
    margin: 0;
    display: flex;
    flex-flow: column nowrap;
    gap: 0.25rem;
    background-color: transparent;
    border: none;
    cursor: pointer;

    &,
    &:hover,
    &:focus {
      color: ${(props) => props.theme.black1000};
      text-decoration: none;
      outline: none;
    }

    & > strong {
      margin: 0;
      padding: 0;
      font-size: 1rem;
      line-height: 1.5;
      font-weight: 500;
      display: flex;
      align-items: flex-start;
      max-width: 100%;

      & > span {
        flex: 0 0 auto;

        &:first-child {
          color: ${(props) => props.theme.redNSP};
        }

        &:nth-child(2) {
          flex: 1 1 auto;
          padding: 0 0.5rem;
        }
      }
    }

    & > span {
      margin: 0;
      padding: 0;
      font-size: 0.875rem;
      font-weight: 500;
      line-height: 1.6;
      color: ${(props) => props.theme.redNSP};
      padding-left: 2rem;
    }
  }
`;

export const MissingDocumentWarning = (props) => {
  const { missingDocumentCount, limitDate, onClick } = props;

  if (!missingDocumentCount) {
    return null;
  }

  return (
    <StyledWarning>
      <button type="button" onClick={onClick}>
        <strong>
          <FeatherIcon name="alert-circle" />
          <span>
            {missingDocumentCount}{" "}
            {missingDocumentCount > 1
              ? "informations requises"
              : "information requise"}{" "}
            sur vos événements publics
          </span>
          <FeatherIcon name="chevron-right" />
        </strong>
        <span>À compléter avant le {displayShortDate(limitDate)}</span>
      </button>
    </StyledWarning>
  );
};

MissingDocumentWarning.propTypes = {
  missingDocumentCount: PropTypes.number,
  limitDate: PropTypes.string,
  onClick: PropTypes.func.isRequired,
};

export default MissingDocumentWarning;
