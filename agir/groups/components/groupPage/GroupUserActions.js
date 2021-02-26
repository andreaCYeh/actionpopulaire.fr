import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";
import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";
import Popin from "@agir/front/genericComponents/Popin";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

const StyledList = styled.ul`
  width: 100%;
  cursor: pointer;
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  list-style: none;
  color: ${style.primary500};
  padding: 0;

  @media (max-width: ${style.collapse}px) {
    margin: 0;
    padding: 1.5rem;
  }

  a {
    display: flex;
    align-items: center;
    border: none;
    padding: 0;
    margin: 0;
    text-decoration: none;
    background: inherit;
    cursor: pointer;
    text-align: center;
    -webkit-appearance: none;
    -moz-appearance: none;
    font-size: 0.875rem;
    line-height: 20px;
    font-weight: 400;
    color: ${style.black1000};
    margin-bottom: 0.5rem;

    &:last-child {
      margin-bottom: 0;
    }

    &:hover,
    &:focus {
      text-decoration: underline;
      border: none;
      outline: none;
    }

    &[disabled],
    &[disabled]:hover,
    &[disabled]:focus {
      opacity: 0.75;
      text-decoration: none;
      cursor: default;
    }

    @media (max-width: ${style.collapse}px) {
      margin-bottom: 1.5rem;
      text-decoration: none;
    }

    & > *:first-child {
      margin-right: 0.5rem;
      width: 1rem;
      height: 1rem;

      @media (max-width: ${style.collapse}px) {
        margin-right: 1rem;-
        width: 1.5rem;
        height: 1.5rem;
      }

      svg {
        width: inherit;
        height: inherit;
        stroke-width: 2;
      }
    }
  }
`;
const StyledPanel = styled.div`
  width: 100%;
  background-color: ${style.primary100};
  padding: 1.5rem;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }

  h6 {
    margin: 0;
    font-size: 1rem;
    line-height: 1;
    color: ${style.primary500};
    margin-bottom: 1rem;
    font-weight: bold;
  }

  && ul {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      font-size: 0.813rem;
      line-height: 1.3;
      display: flex;
      align-items: baseline;

      a {
        color: ${style.black1000};
        margin-left: 0.5rem;
      }
    }

    li + li {
      margin-top: 0.5rem;
    }

    li {
      align-items: center;
      font-weight: normal;
      font-size: 0.875rem;

      a {
        margin-left: 0.5rem;
      }

      ${RawFeatherIcon} {
        svg {
          stroke-width: 2px;
          width: 1rem;
          height: 1rem;
        }
      }
    }
  }

  ${Button} + ul {
    margin-top: 1rem;
  }

  & ~ ${Button} {
    @media (min-width: ${style.collapse}px) {
      display: none;
    }
  }
`;
const StyledContent = styled.div`
  padding: 0;
  display: flex;
  align-items: flex-start;
  flex-flow: column nowrap;
  margin-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    background-color: white;
    width: 100%;
    padding: 0 1rem 1.5rem;
    margin-bottom: 0;
    align-items: center;
    display: ${({ hideOnMobile }) => (hideOnMobile ? "none" : "flex")};
  }

  & > ${Button} {
    margin: 0;
    width: 100%;
    justify-content: center;
  }

  & > ${Button} + ${Button} {
    margin-top: 0.75rem;
  }

  p {
    margin-top: 0.5rem;
    font-weight: 500;
    font-size: 0.813rem;
    line-height: 1.5;
    color: ${style.black500};
    margin-bottom: 0;

    @media (max-width: ${style.collapse}px) {
      font-size: 0.688rem;
      font-weight: 400;
      color: ${style.black1000};
    }
  }
`;

const StyledAdminButton = styled.div`
  width: 100%;
  margin-bottom: 0.75rem;
  text-align: center;

  ${Button} {
    justify-content: center;
    width: 100%;
    cursor: pointer;

    @media (max-width: ${style.collapse}px) {
      width: auto;
    }
  }
`;

const ManagerActions = (props) => {
  const { is2022 = false, routes } = props;

  return (
    <StyledContent>
      <StyledPanel>
        <h6>Gestion du groupe</h6>
        {routes.createEvent && (
          <Button
            as="a"
            href={routes.createEvent}
            color="primary"
            icon="plus"
            small
            inline
          >
            Créer un événement {is2022 ? "de l'équipe" : "du groupe"}
          </Button>
        )}
        <ul>
          {routes.members && (
            <li>
              <RawFeatherIcon
                small
                inline
                color={style.primary500}
                name="users"
              />
              <a href={routes.members}>Membres</a>
            </li>
          )}
          {routes.settings && (
            <li>
              <RawFeatherIcon
                inline
                small
                name="file-text"
                color={style.primary500}
              />
              <a href={routes.settings}>Informations</a>
            </li>
          )}
          {routes.members && (
            <li>
              <RawFeatherIcon
                small
                inline
                color={style.primary500}
                name="lock"
              />
              <a href={routes.members}>Animateur·ices et gestionnaires</a>
            </li>
          )}
          {routes.financement && (
            <li>
              <RawFeatherIcon
                small
                inline
                color={style.primary500}
                name="folder"
              />
              <a href={routes.financement}>Remboursement et dépense</a>
            </li>
          )}
          {routes.certification && (
            <li>
              <RawFeatherIcon
                small
                inline
                color={style.primary500}
                name="check-circle"
              />
              <a href={routes.certification}>Certification</a>
            </li>
          )}
          {routes.financement && (
            <li>
              <RawFeatherIcon
                small
                inline
                color={style.primary500}
                name="loader"
              />
              <a href={routes.financement}>Financement</a>
            </li>
          )}
          {routes.invitation && (
            <li>
              <RawFeatherIcon
                small
                inline
                color={style.primary500}
                name="users"
              />
              <a href={routes.invitation}>Inviter</a>
            </li>
          )}
        </ul>
      </StyledPanel>
      <Button
        as="a"
        href={routes.createEvent}
        color="primary"
        icon="plus"
        small
      >
        Créer un événement {is2022 ? "de l'équipe" : "du groupe"}
      </Button>
      <Button as="a" href={routes.settings} icon="settings" small>
        Gestion {is2022 ? "de l'équipe" : "du groupe"}
      </Button>
    </StyledContent>
  );
};

const MobileMemberActions = (props) => {
  const { is2022 = false, routes, isMenuOpen, openMenu, closeMenu } = props;

  return (
    <div
      style={{
        width: "100%",
        position: "relative",
        margin: "0 0 1rem",
        textAlign: "center",
      }}
    >
      <Button onClick={openMenu} color="default" icon="check" small>
        Vous êtes membre {is2022 ? "de l'équipe" : "du groupe"}
      </Button>
      <BottomSheet isOpen={isMenuOpen} onDismiss={closeMenu} position="bottom">
        <StyledList>
          <li>
            <a href={routes.quit}>
              <FeatherIcon small inline color={style.primary500} name="users" />
              Quitter {is2022 ? "l'équipe" : "le groupe"}
            </a>
          </li>
        </StyledList>
      </BottomSheet>
    </div>
  );
};
const DesktopMemberActions = (props) => {
  const { is2022 = false, routes, isMenuOpen, openMenu, closeMenu } = props;

  return (
    <div
      style={{
        width: "100%",
        position: "relative",
        margin: "0",
      }}
    >
      <Button onClick={openMenu} color="default" icon="check">
        Vous êtes membre {is2022 ? "de l'équipe" : "du groupe"}
      </Button>
      <Popin isOpen={isMenuOpen} onDismiss={closeMenu} position="bottom">
        <StyledList>
          <li>
            <a href={routes.quit}>
              <FeatherIcon small inline color={style.primary500} name="users" />
              Quitter {is2022 ? "l'équipe" : "le groupe"}
            </a>
          </li>
        </StyledList>
      </Popin>
    </div>
  );
};
DesktopMemberActions.propTypes = MobileMemberActions.propTypes = {
  is2022: PropTypes.bool,
  routes: PropTypes.object,
  isMenuOpen: PropTypes.bool,
  openMenu: PropTypes.func,
  closeMenu: PropTypes.func,
};
const MemberActions = (props) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const openMenu = useCallback(() => setIsMenuOpen(true), []);
  const closeMenu = useCallback(() => setIsMenuOpen(false), []);

  return (
    <StyledContent>
      <ResponsiveLayout
        {...props}
        MobileLayout={MobileMemberActions}
        DesktopLayout={DesktopMemberActions}
        isMenuOpen={isMenuOpen}
        openMenu={openMenu}
        closeMenu={closeMenu}
      />
    </StyledContent>
  );
};

const NonMemberActions = (props) => {
  const { is2022 = false, routes } = props;

  return (
    <StyledContent>
      <CSRFProtectedForm method="post" action={(routes && routes.join) || ""}>
        <input type="hidden" name="action" value="join" />
        <Button type="submit" color="success">
          Rejoindre {is2022 ? "l'équipe" : "le groupe"}
        </Button>
      </CSRFProtectedForm>
      <p>Votre email sera communiqué aux animateur·ices</p>
    </StyledContent>
  );
};

const GroupUserActions = (props) => {
  if (props.isManager) {
    return <ManagerActions {...props} />;
  }
  if (props.isMember) {
    return <MemberActions {...props} />;
  }
  return <NonMemberActions {...props} />;
};

ManagerActions.propTypes = MemberActions.propTypes = NonMemberActions.propTypes = GroupUserActions.propTypes = {
  isMember: PropTypes.bool,
  isManager: PropTypes.bool,
  is2022: PropTypes.bool,
  routes: PropTypes.object,
};
export default GroupUserActions;
