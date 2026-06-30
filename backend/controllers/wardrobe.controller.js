import User from "../models/user.model.js";


export const addItem = async (req, res) => {
    try {
        const { name, category, color, occasion, season, emoji } = req.body;

        if (!name || !category || !color)
            return res.status(400).json({ error: "Name, category and color are required" });

        const user = await User.findById(req.user._id);
        
        user.wardrobe.push({ name, category, color, occasion, season, emoji });

        //wardrobe is an array inside user document , .push() adds new item to that array, similar to list.append() in python
        await user.save();

        res.status(201).json({ 
            message: "Item added!",
            wardrobe: user.wardrobe 
        });

    } catch (error) {
        res.status(500).json({ error: "Internal server error" });
    }
};

export const getWardrobe = async (req, res) => {
    try {
        const user = await User.findById(req.user._id).select("wardrobe");

//     WITHOUT minus sign → include ONLY wardrobe
// returns just the wardrobe array
// no need to send full user object

        res.status(200).json(user.wardrobe);
    } catch (error) {
        res.status(500).json({ error: "Internal server error" });
    }
};


export const deleteItem = async (req, res) => {
    try {
        const { itemId } = req.params;
        const user = await User.findById(req.user._id);

        user.wardrobe = user.wardrobe.filter(
            item => item._id.toString() !== itemId
        );

        await user.save();
        res.status(200).json({ 
            message: "Item deleted!",
            wardrobe: user.wardrobe 
        });

    } catch (error) {
        res.status(500).json({ error: "Internal server error" });
    }
};