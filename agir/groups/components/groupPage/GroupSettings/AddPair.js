import React from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const Member = styled.div`
  font-size: 1rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  color: ${style.primary500};
  cursor: pointer;
`;

const AddPair = ({ onClick }) => {

  const handleClick = () => {
    onClick();
    console.log("add pair organizer");
  };
  return (
    <Member onClick={handleClick}>
      <RawFeatherIcon
        name="plus"
        width="1.5rem"
        height="1.5rem"
        style={{
          padding: "0.25rem",
          backgroundColor: style.primary100,
          color: style.primary500,
          borderRadius: "40px",
          marginRight: "1rem",
        }}
      />
      <span>Ajouter votre binôme</span>
    </Member>
  );
};

export default AddPair;
