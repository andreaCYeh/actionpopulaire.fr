import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer";
import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import checkCirclePrimary from "@agir/front/genericComponents/images/check-circle-primary.svg";

import { updateProfile } from "@agir/front/authentication/api";

const Container = styled.form`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 7rem 2rem 1.5rem;
  width: 100%;
  margin: 0 auto;

  @media (max-width: ${style.collapse}px) {
    max-width: 400px;
    padding: 3rem 2rem 1.5rem;
    text-align: left;
  }

  h2,
  p {
    margin: 0;
    max-width: 100%;
  }

  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    line-height: 1.5;

    @media (max-width: ${style.collapse}px) {
      font-size: 1.125rem;
    }

    span {
      display: block;
    }
  }

  & > ${Button} {
    margin: 0;
    width: 100%;
    max-width: 356px;
    justify-content: center;

    &[type="button"] {
      background-color: transparent;
      color: ${style.black500};
      font-size: 0.875rem;
      font-weight: 400;
    }
  }
`;

const RadioBlock = styled.div`
  width: 250px;
  display: flex;
  flex-align: center;
  text-align: center;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 1.5rem;
  position: relative;
  cursor: pointer;
  transition: ease 0.2s;

  @media (max-width: ${style.collapse}px) {
    flex-direction: row;
    justify-content: flex-start;
    width: 100%;
    text-align: left;
  }

  &.responsive-margin {
    @media (max-width: ${style.collapse}px) {
      margin-top: 1rem;
    }
    @media (min-width: ${style.collapse}px) {
      margin-left: 1.5rem;
    }
  }

  ${(props) => {
    if (props.$checked) {
      return `
        border 1px solid ${style.primary500};
        box-shadow: 0px 0px 3px ${style.primary500}, 0px 2px 0px rgba(87, 26, 255, 0.2);
        `;
    } else {
      return `
        border: 1px solid #C4C4C4;
      `;
    }
  }};

  &:hover {
    border-color: ${style.primary500};
  }

  > div {
    position: absolute;
    right: 12px;
    top: 12px;
    margin: 0px;
  }
  input {
    position: absolute;
    right: 12px;
    top: 12px;
    margin: 0px;
    border: 1px solid #333;
  }
  span {
    ${(props) => props.$checked && `color: ${style.primary500}`};
    margin-top: 14px;
    padding: 10px;
    font-weight: 600;
    font-size: 1rem;

    @media (max-width: ${style.collapse}px) {
      margin-top: 0;
    }
  }
  img {
    width: 114px;

    @media (max-width: ${style.collapse}px) {
      width: 80px;
    }
  }
`;

const InputRadio = styled.div`
  div {
    width: 1.3rem;
    height: 1.3rem;
    border: 1px solid #000a2c;
    border-radius: 20px;
  }
  img {
    width: 1.3rem;
  }
`;

const NEWSLETTER_OPTIONS = [
  {
    label: "Grands événements de la campagne",
    value: "2022_exceptionnel",
    selected: true,
  },
  {
    label: "Lettres d'informations, environ une fois par semaine",
    value: "2022",
    selected: true,
  },
  {
    label: "Actions en ligne",
    value: "2022_en_ligne",
    selected: false,
  },
  {
    label: "Agir près de chez moi",
    value: "2022_chez_moi",
    selected: false,
  },
  {
    label: "L’actualité sur le programme",
    value: "2022_programme",
    selected: false,
  },
  /*{
    label: "Recevez des informations sur la France insoumise",
    value: "LFI",
    selected: false,
  },*/
];

const CampaignOption = (props) => {
  const { value, img, label, selected, onChange } = props;

  const handleChange = useCallback(() => {
    onChange && onChange(value);
  }, [value, onChange]);
  return (
    <RadioBlock onClick={handleChange} $checked={selected}>
      <img src={img} width="114" height="114" alt="Jean-Luc Mélenchon" />
      <span>{label}</span>
      <InputRadio>
        {selected ? (
          <img src={checkCirclePrimary} width="16" height="16" />
        ) : (
          <div />
        )}
      </InputRadio>
    </RadioBlock>
  );
};
CampaignOption.propTypes = {
  value: PropTypes.string,
  label: PropTypes.string,
  img: PropTypes.string,
  selected: PropTypes.bool,
  onChange: PropTypes.func,
};

const NewsletterOption = (props) => {
  const { value, label, selected, onChange } = props;

  const handleChange = useCallback(
    (e) => {
      onChange && onChange(value, e.target.checked);
    },
    [value, onChange]
  );

  return (
    <CheckboxField
      name={value}
      label={label}
      value={selected}
      onChange={handleChange}
    />
  );
};
NewsletterOption.propTypes = {
  value: PropTypes.string,
  label: PropTypes.string,
  selected: PropTypes.bool,
  onChange: PropTypes.func,
};

const ChooseNewsletters = ({ dismiss }) => {
  const [newsletters, setNewsletters] = useState([]);
  const [submitted, setSubmitted] = useState(false);

  const handleChangeNewsletter = useCallback((value, checked) => {
    if (checked) {
      setNewsletters((state) => [...state, value]);
    } else {
      setNewsletters((state) => state.filter((item) => item !== value));
    }
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setSubmitted(true);
      await updateProfile({ newsletters });
      await dismiss();
      setSubmitted(false);
    },
    [dismiss, newsletters]
  );

  useEffect(() => {
    setNewsletters(
      NEWSLETTER_OPTIONS.filter((option) => option.selected).map(
        (option) => option.value
      )
    );
  }, []);

  return (
    <div>
      <Hide under>
        <div style={{ position: "fixed" }}>
          <Link route="events">
            <LogoAP
              style={{ marginTop: "2rem", paddingLeft: "2rem", width: "200px" }}
            />
          </Link>
        </div>
      </Hide>
      <Container onSubmit={handleSubmit}>
        <h2>Recevez des informations sur la campagne</h2>
        <Spacer size="1rem" />
        <p>Nous vous suggérerons des actions qui vous intéressent</p>
        <Spacer size="2rem" />
        <div style={{ textAlign: "left" }}>
          {NEWSLETTER_OPTIONS.map((option) => (
            <NewsletterOption
              key={option.value}
              {...option}
              selected={newsletters.includes(option.value)}
              onChange={handleChangeNewsletter}
            />
          ))}
        </div>
        <Spacer size="2rem" />
        <Button color="primary" type="submit" disabled={submitted}>
          Continuer
        </Button>
        <Spacer size="1rem" />
        <Button type="button" onClick={dismiss} disabled={submitted}>
          Passer cette étape
        </Button>
      </Container>
    </div>
  );
};
ChooseNewsletters.propTypes = {
  dismiss: PropTypes.func.isRequired,
};
export default ChooseNewsletters;
