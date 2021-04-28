import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import { Column, Row } from "@agir/front/genericComponents/grid";

import { inviteToGroup } from "@agir/groups/groupPage/api.js";

const StyledContainer = styled.div`
  display: flex;
  align-items: center;

  & > :first-child {
    max-width: 300px;
    width: 100%;
  }

  @media (max-width: ${style.collapse}px) {
    flex-wrap: wrap;
    & > :first-child {
      width: 100%;
    }
  }
`;

const StyledDiv = styled.div`
  font-weight: 500;
`;

const GroupInvitation = (props) => {
  const { title, groupPk } = props;

  const [email, setEmail] = useState("");
  const [errors, setErrors] = useState({});

  const handleChange = useCallback((e) => {
    setEmail(e.target.value);
  }, []);

  const handleInvitation = useCallback(
    async (e) => {
      e.preventDefault();
      setErrors({});
      const res = await inviteToGroup(groupPk, { email });
      if (!!res.error) {
        setErrors(res.error);
        return;
      }
      setEmail("");
    },
    [email]
  );

  return (
    <StyledDiv>
      <Row gutter={2} style={{ marginBottom: "1rem" }}>
        <Column grow collapse={false}>
          {title}
        </Column>
      </Row>

      <StyledContainer>
        <div style={{ marginRight: "0.5rem" }}>
          <TextField
            type="text"
            value={email}
            placeholder="Adresse e-mail de l’invité·e"
            onChange={handleChange}
            error={errors?.email}
          />
        </div>
        <div>
          <Button color="primary" small onClick={handleInvitation}>
            Envoyer une invitation
          </Button>
        </div>
      </StyledContainer>
    </StyledDiv>
  );
};
GroupInvitation.propTypes = {
  title: PropTypes.string,
};
export default GroupInvitation;
