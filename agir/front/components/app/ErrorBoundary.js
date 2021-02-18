import PropTypes from "prop-types";
import React from "react";

import generateLogger from "@agir/lib/utils/logger";

const logger = generateLogger(__filename);

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      errorMessage: "",
    };
  }

  static getDerivedStateFromError(error) {
    return {
      errorMessage: error.toString(),
    };
  }

  componentDidCatch(error, info) {
    logger.debug(error, info);
  }

  render() {
    const { children, Fallback } = this.props;

    const { errorMessage } = this.state;

    if (!errorMessage) {
      return children;
    }
    if (Fallback) {
      return <Fallback {...this.props} errorMessage={errorMessage} />;
    }

    return (
      <div>
        <h2>
          Une erreur est survenue. Nous faisons notre possible pour la corriger.
        </h2>
        {process.env.NODE_ENV === "production" ? null : <p>{errorMessage}</p>}
      </div>
    );
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node,
  Fallback: PropTypes.oneOfType([PropTypes.func, PropTypes.element]),
};

export default ErrorBoundary;
