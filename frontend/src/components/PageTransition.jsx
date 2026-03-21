import React from 'react';
import { motion } from 'framer-motion';

const pageVariants = {
  initial: { opacity: 0, y: 30, scale: 0.98, rotateX: 5 },
  in: { opacity: 1, y: 0, scale: 1, rotateX: 0 },
  out: { opacity: 0, y: -30, scale: 1.02, rotateX: -5 }
};

const pageTransition = {
  type: 'spring',
  stiffness: 120,
  damping: 20
};

export default function PageTransition({ children }) {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
      style={{ transformPerspective: 1000 }} // Gives the 3D depth effect
    >
      {children}
    </motion.div>
  );
}
