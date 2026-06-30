import mongoose from "mongoose";

// SQLAlchemy  → helps Python talk to SQL databases
// mongoose    → helps Node.js talk to MongoDB


const connectMONGODB = async () => {
    try {
        const conn = await mongoose.connect(process.env.MONGO_URI);
        console.log(`MongoDB connected: ${conn.connection.host}`);
    }
    catch(error) {
        console.error(`Error connecting to MongoDB: ${error.message}`);
        process.exit(1);
        // 1 mweans stopped with an error
    }
}

export default connectMONGODB;
// make this function available to other files

