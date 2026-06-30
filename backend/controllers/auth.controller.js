import User from "../models/user.model.js"; // brings in User model to interact with MongoDB
import bcrypt from "bcryptjs"; // password hashing library — converts "mypassword123" to "$2a$10$xK8..."
import { generateTokenAndSetCookie } from "../lib/utils/generateToken.js"; // token function

//SIGNUP
export const signup = async (req, res) => { // async because we talk to database
    try {
        const { fullname, username, email, password ,city} = req.body; // extract fields from form submission

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // pattern that valid emails must match
        if (!emailRegex.test(email)) { 
            return res.status(400).json({ error: "Invalid email format" }); // 400 = bad request
        }

        const existingUser = await User.findOne({ username }); // search MongoDB for this username
        if (existingUser) { // if found, username is taken
            return res.status(400).json({ error: "Username already taken" }); // 
        }

        const existingEmail = await User.findOne({ email }); // search MongoDB for this email
        if (existingEmail) { // if found → email is taken
            return res.status(400).json({ error: "Email already taken" }); // stop, send error
        }

        if (password.length < 6) { // check password is long
            return res.status(400).json({ error: "Password must be at least 6 characters" }); // stop, send error
        }

        const salt = await bcrypt.genSalt(10); // generate random salt — makes every hash unique
        const hashedPassword = await bcrypt.hash(password, salt); // combine password + salt = hash

        const newUser = new User({ // create new user OBJECT in memory, not saved yet
            fullname, // fullname: fullname
            username, //username: username
            email,    // email: email
            password: hashedPassword, 
            city:city||"Delhi",
        });

        await newUser.save(); // save to database
        generateTokenAndSetCookie(newUser._id, res); // create JWT token + set cookie → user is logged in

        res.status(201).json({ // 201 = created successfully
            _id: newUser._id,         // MongoDB auto-generated unique ID
            fullname: newUser.fullname,
            username: newUser.username,
            email: newUser.email,

            // no password — never send password to frontend
            city:newUser.city,
        });

    } catch (error) {
       console.log("Signup error:", error.message);
        res.status(500).json({ error: "Internal server error" }); // 500 = server crashed
    }
};

//LOGIN
export const login = async (req, res) => {
    try {
        const { username, password } = req.body;
        const user = await User.findOne({ username });

        if (!user || !await bcrypt.compare(password, user.password))
            return res.status(400).json({ error: "Invalid username or password" });

        generateTokenAndSetCookie(user._id, res);
        res.status(200).json({
            _id:      user._id,
            fullname: user.fullname,
            username: user.username,
            email:    user.email,
            city:user.city,
        });

    } catch (error) {
        res.status(500).json({ error: "Internal server error" });
    }
};

//LOGOUT
export const logout= async(req,res)=>{
try {
    res.cookie("jwt","",{maxAge:0})
    //means the cookie with name jwt returns an empty string as its value 
    //and maxAge means the cookie expires immediately 
    res.status(200).json({message:"Logged out successfully"});

    
} catch (error) {
    
    res.status(500).json({error:"Internal server Error"});

}
};


//GET CURRENT USER
export const getMe = async (req, res) => {
    try {
        const user = await User.findById(req.user._id).select("-password");
        // req.user._id → set by protectRoute middleware, we know who is logged in
        // findById()   → get fresh user data from MongoDB
        // .select("-password") → exclude password from response

        res.status(200).json(user); // send user data to frontend

    } catch (error) {
        res.status(500).json({ error: "Internal server error" });
    }
};