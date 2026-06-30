import mongoose from "mongoose";


const WardrobeItemSchema = new mongoose.Schema({
    name:     { type: String, required: true },
    category: { type: String, required: true },
    color:    { type: String, required: true },
    occasion: { type: String, default: "casual" },
    season:   { type: String, default: "all" },
    emoji:    { type: String, default: "👕" },
    
});


const UserSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    fullname: { type: String, required: true },
    email:    { type: String, required: true, unique: true },
    password: { type: String, required: true },
    city:{type:String,default:"Delhi"},
    wardrobe: [WardrobeItemSchema], //array of wardrobe items
}, { timestamps: true });

const User = mongoose.model("User", UserSchema);
export default User;