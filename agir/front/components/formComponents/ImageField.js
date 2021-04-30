import PropTypes from "prop-types";
import React, { forwardRef } from "react";

import Button from "@agir/front/genericComponents/Button";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledError = styled.span`
  color: ${style.redNSP};
`;

const StyledField = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;

  label {
    flex: 0 0 auto;
    display: flex;
    flex-flow: column nowrap;
    align-items: flex-start;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;

    & > * {
      margin: 0;
    }

    ${StyledLabel} {
      font-weight: 600;
    }

    input[type="file"] {
      display: none;
    }

    ${Button} {
      width: auto;
      margin-top: 0.5rem;
    }
  }
`;

const ImageField = forwardRef((props, ref) => {
  const {
    id,
    name,
    value,
    onChange,
    onDelete,
    error,
    label,
    helpText,
    ...rest
  } = props;

  const labelRef = React.useRef(null);
  const handleChange = React.useCallback(
    (e) => {
      e?.target?.files &&
        onChange &&
        onChange(e.target.files[e.target.files.length - 1]);
    },
    [onChange]
  );

  const handleClick = React.useCallback(() => {
    labelRef.current && labelRef.current.click();
  }, []);

  const thumbnail = React.useMemo(() => {
    if (typeof value === "string") {
      return value;
    }
    if (value && value.name) {
      return URL.createObjectURL(value);
    }

    return null;
  }, [value]);

  const imageName = React.useMemo(() => {
    if (typeof value === "string") {
      return value;
    }
    if (value && value.name) {
      return value.name;
    }

    return "";
  }, [value]);

  return (
    <>
      <StyledField $valid={!error} $invalid={!!error} $empty={!!value}>
        {imageName && (
          <>
            <img
              src={thumbnail}
              alt=""
              style={{ maxWidth: "178px", maxHeight: "100px", marginRight: "1.5rem" }}
            />
          </>
        )}
        <label htmlFor={id} ref={labelRef}>
          {label && <StyledLabel>{label}</StyledLabel>}
          {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
          <input
            {...rest}
            ref={ref}
            id={id}
            name={name}
            type="file"
            onChange={handleChange}
          />
          <Button type="button" inline $wrap onClick={handleClick}>
            <RawFeatherIcon name="camera" style={{ marginRight: "0.5rem" }} />
            {imageName ? "Remplacer l'image" : "Ajouter une image"}
          </Button>
          {imageName && onDelete && (
            <a href="#" onClick={onDelete} style={{ marginTop: "0.5rem" }}>
              Supprimer l'image
            </a>
          )}
        </label>
      </StyledField>
      {!!error && <StyledError>{error}</StyledError>}
    </>
  );
});

ImageField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  onDelete: PropTypes.func,
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
};

ImageField.displayName = "ImageField";

export default ImageField;
