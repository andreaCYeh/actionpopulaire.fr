import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { InfosElu } from "@agir/elus/parrainages/types";
import { StatutPill } from "./types";

const ResultBoxLayout = styled.ul`
  display: block;
  margin: 0;
  padding: 0;
  background-color: ${(props) => props.theme.black25};

  li {
  }

  li + li {
    border-top: 1px solid ${(props) => props.theme.black50};
  }

  strong {
    font-size: 1rem;
    font-weight: 600;
  }
`;

const Button = styled.button`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
  background-color: ${(props) => props.theme.black25};

  border: 0;
  margin: 0;
  padding: 1rem;

  border-left: 3px solid
    ${(props) =>
      props.selected ? props.theme.primary500 : props.theme.black25};

  text-align: left;
  width: 100%;
`;

const ResultBox = ({ elus, onSelect, selected }) => {
  return (
    <ResultBoxLayout>
      {elus.map((elu) => (
        <li key={elu.id}>
          <Button selected={elu === selected} onClick={() => onSelect(elu)}>
            <div>
              <strong>{elu.nomComplet}</strong>
              <br />
              {elu.commune}
            </div>
            <StatutPill statut={elu.statut} />
          </Button>
        </li>
      ))}
    </ResultBoxLayout>
  );
};

ResultBox.propTypes = {
  elus: PropTypes.arrayOf(InfosElu),
  onSelect: PropTypes.func,
  selected: InfosElu,
};
ResultBox.defaultProps = {
  elus: [],
  onSelect: () => {},
};
ResultBox.Layout = ResultBoxLayout;

export default ResultBox;
