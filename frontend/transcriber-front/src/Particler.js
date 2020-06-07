import React from "react";

import Particles from "react-particles-js";

const Particler = () => (
  <Particles
    params={{
      particles: {
        number: {
          value: 120,
          density: {
            enable: true,
            value_area: 1000,
          },
        },
        color: {
          value: "#264b77",
        },
        lineLinked: {
          enable: true,
          // distance: 300,
          color: "#264b77",
          opacity: 0.3,
          width: 1.4,
        },
      },
    }}
  />
);

export default Particler;
