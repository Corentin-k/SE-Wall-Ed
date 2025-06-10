<template>
  <div ref="lottieContainer"></div>
</template>

<script>
import lottie from "lottie-web"; // Importer Lottie Web
import animationData from "@/assets/Animation - 1721226223724.json"; // Chemin vers votre fichier .json

export default {
  name: "LottieAnimation",
  mounted() {
    // Initialiser Lottie
    const animationContainer = this.$refs.lottieContainer;
    lottie.loadAnimation({
      container: animationContainer,
      renderer: "svg", // Choisissez le rendu SVG ou HTML (facultatif)
      loop: true, // Optionnel : Définir la boucle
      autoplay: true, // Optionnel : Lecture automatique de l'animation
      animationData: animationData, // Charger les données d'animation à partir du fichier .json
    });
  },
};
</script>

<style scoped>
/* Styles spécifiques au conteneur de l'animation */
.lottie-container {
  width: 100%;
  height: 100%;
}
</style>
