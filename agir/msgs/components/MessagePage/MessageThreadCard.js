import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { getMessageSubject } from "@agir/msgs/common/utils";
import { timeAgo } from "@agir/lib/utils/time";

import Avatars from "@agir/front/genericComponents/Avatars";
import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import { StyledCard } from "./styledComponents";

const StyledUnreadItemBadge = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  background-color: ${style.redNSP};
  text-align: center;
  border-radius: 100%;
  font-weight: 700;
  font-size: 0.813rem;
  line-height: 0;
  color: ${({ $empty }) => ($empty ? style.redNSP : style.white)};
  opacity: ${({ $empty }) => ($empty ? "0" : "1")};
  transform: scale(${({ $empty }) => ($empty ? "0" : "1")});
  transition: color, opacity, transform 150ms ease-out;
  will-change: color, opacity, transform;
`;

const MessageThreadCard = (props) => {
  const { message, isLoading, isSelected, onClick } = props;

  const {
    id,
    author,
    group,
    isUnread,
    unreadCommentCount,
    lastComment,
    lastUpdate,
    requiredMembershipType,
  } = message;

  const isOrganizationMessage =
    requiredMembershipType > MEMBERSHIP_TYPES.MEMBER;

  const handleClick = useCallback(() => {
    onClick && onClick(id);
  }, [onClick, id]);

  const unreadItemCount = (isUnread ? 1 : 0) + (unreadCommentCount || 0);
  let subject = getMessageSubject(message);
  if (isOrganizationMessage && !subject) {
    subject = message.author.displayName;
    if (group.referents.length > 1) {
      subject += ", ";
    } else {
      subject += " et ";
    }
    subject += group.referents[0].displayName;
    if (group.referents.length > 1) {
      subject += ` et ${group.referents[1].displayName}`;
    }
  }
  const time = timeAgo(lastUpdate).replace("il y a", "");
  const text = lastComment
    ? `${lastComment.author.displayName} : ${lastComment.text}`
    : `${message.author.displayName} : ${message.text}`;
  const authors =
    author.id && lastComment?.author && lastComment.author.id !== author.id
      ? [author, lastComment.author]
      : [author];

  return (
    <StyledCard
      type="button"
      onClick={handleClick}
      $selected={isSelected}
      isOrganizationMessage={isOrganizationMessage}
      disabled={isLoading}
    >
      <Avatars people={authors} />
      <article>
        <h6 title={group.name}>{group.name}</h6>
        <h5 title={subject}>{subject}</h5>
        {!isOrganizationMessage && (
          <p title={text}>
            <span>{text}</span>
            <span>&nbsp;•&nbsp;{time}</span>
          </p>
        )}
      </article>
      <StyledUnreadItemBadge
        aria-label="Nombre de commentaires non lus"
        $empty={unreadItemCount === 0}
      >
        {unreadItemCount}
      </StyledUnreadItemBadge>
    </StyledCard>
  );
};

MessageThreadCard.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    created: PropTypes.string.isRequired,
    subject: PropTypes.string,
    author: PropTypes.shape({
      id: PropTypes.string,
      displayName: PropTypes.string.isRequired,
      image: PropTypes.string,
    }).isRequired,
    group: PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
    }).isRequired,
    text: PropTypes.string.isRequired,
    lastUpdate: PropTypes.string.isRequired,
    lastComment: PropTypes.shape({
      id: PropTypes.string.isRequired,
      created: PropTypes.string.isRequired,
      author: PropTypes.shape({
        id: PropTypes.string,
        displayName: PropTypes.string.isRequired,
        image: PropTypes.string,
      }).isRequired,
      text: PropTypes.string.isRequired,
    }),
    unreadCommentCount: PropTypes.number,
    isUnread: PropTypes.bool,
  }).isRequired,
  isLoading: PropTypes.bool,
  isSelected: PropTypes.bool,
  onClick: PropTypes.func,
};

export default MessageThreadCard;
