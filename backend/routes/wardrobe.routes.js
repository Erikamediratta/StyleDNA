import express from "express";
import { addItem, getWardrobe, deleteItem } from "../controllers/wardrobe.controller.js";
import { protectRoute } from "../middleware/protectRoute.js";

const router = express.Router();

router.post("/add", protectRoute, addItem);
router.get("/", protectRoute, getWardrobe);
router.delete("/:itemId", protectRoute, deleteItem);

export default router;