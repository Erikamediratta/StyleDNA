// Normal route:
// Request → Route Handler → Response

// Route with middleware:
// Request → Middleware → Route Handler → Response

// Middleware is a checkpoint.
// Like security at an airport:
// → you can't board the plane (route handler)
// → without passing security (middleware)

// protectRoute is our security checkpoint.
// "Are you logged in? Show me your token."

import jwt from "jsonwebtoken";
import User from "../models/user.model.js";

export const protectRoute=async (req,res,next)=>{
    try{
    const token =req.cookies.jwt;

    if(!token){
        return res.status(401).json({error:"Not authorized"});

    }
    const decoded=jwt.verify(token,process.env.JWT_SECRET);

    const user= await User.findById(decoded.userId).select("-password");

    if(!user)
    {
        return res.status(401).json({error:"User not found"});
    }



    req.user=user;

//     we need to pass the user data
// from protectRoute → to the route handler

    next();
}
catch(error)
{
    res.status(500).json({error:"Internal server error"});
}

}
