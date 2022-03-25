import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "./GroupPageCard";
import Map from "@agir/carte/common/Map";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledMap = styled.div`
  height: 308px;

  @media (max-width: ${style.collapse}px) {
    height: 155px;
  }
`;
const StyledAddress = styled.div`
  margin-top: 1rem;
  margin-bottom: 0;
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;

  &:first-child {
    margin-top: 0;
  }

  p {
    margin-left: 0.5rem;
    margin-bottom: 0;
    display: flex;
    flex-flow: column nowrap;
    font-size: 0.875rem;
    color: ${style.black500};
    line-height: 1.5;
    font-weight: 400;

    span {
      &:first-child {
        font-weight: 500;
        color: ${style.black1000};
      }
    }

    &:last-child {
      margin-left: auto;
    }

    a {
      font-weight: 500;
      text-decoration: none;
      color: ${style.primary500};
    }
  }
`;

const GroupLocation = (props) => {
  const { location, iconConfiguration, groupSettingsLinks } = props;

  if (!location || Object.values(location).filter(Boolean).length === 0) {
    return null;
  }

  const {
    name,
    address1,
    address2,
    city,
    zip,
    countryName,
    country,
    coordinates,
  } = location;

  if (
    !(
      name ||
      address1 ||
      address2 ||
      city ||
      zip ||
      countryName ||
      country ||
      coordinates
    )
  ) {
    return null;
  }

  return (
    <Card title="Accès" editLinkTo={groupSettingsLinks?.location} outlined>
      {coordinates && Array.isArray(coordinates.coordinates) ? (
        <StyledMap>
          <Map
            center={coordinates.coordinates}
            iconConfiguration={iconConfiguration}
            width={552}
            height={308}
          />
        </StyledMap>
      ) : null}
      <StyledAddress>
        <FeatherIcon name="map-pin" small inline />
        <p>
          {name && <span>{name}</span>}
          {address1 && <span>{address1}</span>}
          {address2 && <span>{address2}</span>}
          {(zip || city) && (
            <span>{[zip, city].filter(Boolean).join(" ")}</span>
          )}
          {countryName ? <span>{countryName}</span> : <span>{country}</span>}
        </p>
        <p>
          {coordinates && Array.isArray(coordinates.coordinates) ? (
            <a
              href={`https://www.google.com/maps/dir/?api=1&destination=${
                coordinates.coordinates[1] + "," + coordinates.coordinates[0]
              }`}
              target="_blank"
              rel="noopener noreferrer"
            >
              Itinéraire
            </a>
          ) : null}
        </p>
      </StyledAddress>
    </Card>
  );
};

GroupLocation.propTypes = {
  iconConfiguration: PropTypes.object,
  location: PropTypes.shape({
    name: PropTypes.string,
    address1: PropTypes.string,
    address2: PropTypes.string,
    city: PropTypes.string,
    zip: PropTypes.string,
    country: PropTypes.string,
    countryName: PropTypes.string,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }),
  }).isRequired,
  groupSettingsLinks: PropTypes.shape({
    location: PropTypes.string,
  }),
};
export default GroupLocation;
