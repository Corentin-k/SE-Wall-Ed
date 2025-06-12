// src/plugins/fontawesome.js
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faThermometerHalf, faTint, faSyncAlt } from '@fortawesome/free-solid-svg-icons';

library.add(faThermometerHalf, faTint, faSyncAlt);

export default FontAwesomeIcon;
