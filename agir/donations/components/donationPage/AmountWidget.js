import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import { displayPrice } from "@agir/lib/utils/display";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import ByMonthWidget from "./ByMonthWidget";
import GroupPercentageWidget from "./GroupPercentageWidget";
import { Button, SelectedButton, StyledButtonLabel } from "./StyledComponents";

const DEFAULT_AMOUNTS = [500, 1000, 1500, 3000, 5000];

const StyledAmountGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: auto auto;
  align-items: stretch;
  grid-gap: 0.5rem;
`;

const StyledTaxReduction = styled.p`
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  margin: 1rem 0 2rem;
  border-radius: ${(props) => props.theme.borderRadius};
  border: 1px solid ${(props) => props.theme.black200};
  font-weight: 500;

  span {
    flex: 0 0 auto;
  }

  span + span {
    flex: 1 1 auto;
    margin-left: 0.75rem;
  }

  ${RawFeatherIcon}, strong {
    color: ${(props) => props.theme.green500};
  }

  strong {
    font-weight: 600;
    box-shadow: inset 0 -2px ${(props) => props.theme.green500};
  }
`;

const StyledAmountWidget = styled.div`
  padding: 2rem 0;

  ${Button} {
    font-weight: 600;
  }
`;

const AmountWidget = (props) => {
  const {
    amount,
    groupPercentage,
    byMonth,
    onChangeAmount,
    onChangeGroupPercentage,
    onChangeByMonth,
    disabled,
  } = props;

  const [customAmount, setCustomAmount] = useState(
    amount && !DEFAULT_AMOUNTS.includes(amount) ? amount : 0
  );

  const updateCustomAmount = useCallback(
    (e) => {
      let newAmount = parseFloat(e.target.value || 0);
      if (isNaN(newAmount)) {
        newAmount = 0;
      }
      newAmount = newAmount * 100;
      newAmount = Math.abs(newAmount);
      newAmount = Math.floor(newAmount);
      setCustomAmount(newAmount);
      onChangeAmount(newAmount);
    },
    [onChangeAmount]
  );

  const selectDefaultAmount = useCallback(
    (newAmount) => {
      setCustomAmount(0);
      onChangeAmount(newAmount);
    },
    [onChangeAmount]
  );

  return (
    <StyledAmountWidget>
      <StyledAmountGrid>
        {DEFAULT_AMOUNTS.map((defaultAmount) => (
          <Button
            type="button"
            key={defaultAmount}
            onClick={() => selectDefaultAmount(defaultAmount)}
            disabled={disabled}
            as={
              !customAmount && defaultAmount === amount
                ? SelectedButton
                : Button
            }
          >
            {displayPrice(defaultAmount)}
          </Button>
        ))}
        <StyledButtonLabel
          htmlFor="customAmount"
          aria-label="Montant personnalisé"
          $empty={!customAmount}
          $disabled={disabled}
        >
          <input
            name="customAmount"
            id="customAmount"
            type="number"
            min="0"
            step="1"
            value={customAmount ? customAmount / 100 : ""}
            onChange={updateCustomAmount}
            disabled={disabled}
          />
        </StyledButtonLabel>
      </StyledAmountGrid>
      {amount ? (
        <StyledTaxReduction>
          <RawFeatherIcon name="arrow-right" />
          <span>
            Soit&nbsp;<strong>{displayPrice(amount * 0.34)}</strong>&nbsp;après
            la réduction d'impôt, si vous payez l'impôt sur le revenu&nbsp;!
          </span>
        </StyledTaxReduction>
      ) : null}
      {onChangeGroupPercentage && (
        <GroupPercentageWidget
          value={groupPercentage}
          onChange={onChangeGroupPercentage}
          disabled={disabled}
        />
      )}
      <ByMonthWidget
        value={byMonth}
        onChange={onChangeByMonth}
        disabled={disabled}
      />
    </StyledAmountWidget>
  );
};

AmountWidget.propTypes = {
  amount: PropTypes.number,
  groupPercentage: PropTypes.number,
  byMonth: PropTypes.bool,
  onChangeAmount: PropTypes.func.isRequired,
  onChangeGroupPercentage: PropTypes.func,
  onChangeByMonth: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  error: PropTypes.string,
};

export default AmountWidget;
