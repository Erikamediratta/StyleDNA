import jwt from "jsonwebtoken";

export const generateTokenAndSetCookie= (userId,res)=>{
       const token = jwt.sign(
        {userId},
        process.env.JWT_SECRET,
        {expiresIn:"15d"}
        // token dies after 15 days automatically
// even if hacker steals it → useless after 15 days
// user gets logged out naturally
// much more secure

       );
   res.cookie("jwt",token,{
        httpOnly:true,
        secure:false,
         maxAge: 15 * 24 * 60 * 60 * 1000
         //cookie dies after 15 days ,express cookie works in milliseconds only so its 15days only, must match with expires in
       });
};