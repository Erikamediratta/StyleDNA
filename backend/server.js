import express from "express";
import dotenv from "dotenv";
import cookieParser from "cookie-parser";
import cors from "cors";
import authRoutes from "./routes/auth.routes.js";
import wardrobeRoutes from "./routes/wardrobe.routes.js";
import connectMongoDB from "./DB/connectMongoDB.js";

dotenv.config();

const app = express();

app.use(express.json());
app.use(cookieParser());
app.use(cors({ origin: "http://localhost:5000", credentials: true }));

app.use("/api/auth", authRoutes);
app.use("/api/wardrobe", wardrobeRoutes); 

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
    console.log(`StyleDNA backend running on port ${PORT}`);
    connectMONGODB();
});