import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Avatar from "@agir/front/genericComponents/Avatar";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import style from "@agir/front/genericComponents/_variables.scss";

import { IconLink } from "./StyledBar";
import UserMenu from "../UserMenu";
import { useRouteMatch } from "react-router-dom";
import useSWR from "swr";
import { useToast } from "@agir/front/globalContext/hooks";
import { switchMessageMuted, getGroupEndpoint } from "@agir/groups/api.js";

const BlockMuteMessage = styled.div`
  ${({ isActive }) => !isActive && `color: red;`}
  ${RawFeatherIcon}:hover {
    color: ${style.primary500};
  }
`;

export const RightLink = (props) => {
  const { isLoading, user, settingsLink } = props;
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const sendToast = useToast();
  const matchMessagePage = useRouteMatch("/messages/:messagePk/");
  const messagePk = matchMessagePage?.params.messagePk;
  const { data, mutate } = useSWR(
    getGroupEndpoint("getMessageMuted", { messagePk })
  );

  const switchNotificationMessage = async () => {
    const { data } = await switchMessageMuted({ id: messagePk });
    mutate(() => data);
    let text =
      "Vous ne recevrez plus de notifications reliées à ce fil de messages";
    let type = "INFO";
    if (data.data === "on") {
      text = "Les notifications reliées à ce fil de message sont réactivées";
      type = "SUCCESS";
    }
    sendToast(text, type, { autoClose: true });
  };

  if (isLoading) {
    return <IconLink as={Spacer} size="32px" />;
  }

  if (!user) {
    return (
      <IconLink route="login">
        <RawFeatherIcon name="user" width="24px" height="24px" />
      </IconLink>
    );
  }

  if (settingsLink) {
    const isMessagePage = !!matchMessagePage;
    // Show muted message settings
    if (isMessagePage) {
      const isActive = data && data.data === "on";
      return (
        <BlockMuteMessage isActive={isActive}>
          <RawFeatherIcon
            name={`bell${!isActive ? "-off" : ""}`}
            onClick={switchNotificationMessage}
          />
        </BlockMuteMessage>
      );
    }

    return (
      <IconLink
        to={settingsLink.to}
        href={settingsLink.href}
        route={settingsLink.route}
        title={settingsLink.label}
        aria-label={settingsLink.label}
      >
        <RawFeatherIcon name="settings" width="24px" height="24px" />
      </IconLink>
    );
  }

  const openUserMenu = () => setIsUserMenuOpen(true);
  const closeUserMenu = () => setIsUserMenuOpen(false);

  return (
    <>
      <Avatar
        as="button"
        aria-label="Paramètres du compte"
        onClick={openUserMenu}
        displayName={user.displayName}
        image={user.image}
        style={{
          border: "none",
          width: "32px",
          height: "32px",
        }}
      />
      <BottomSheet
        isOpen={isUserMenuOpen}
        onDismiss={closeUserMenu}
        shouldDismissOnClick
      >
        <UserMenu user={user} />
      </BottomSheet>
    </>
  );
};

RightLink.propTypes = {
  isLoading: PropTypes.bool,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
  settingsLink: PropTypes.object,
};

export default RightLink;
