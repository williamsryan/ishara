import React from "react";

const NewsFeed = ({ news }) => {
    return (
        <div className="news-feed">
            <h3>Market News</h3>
            <ul>
                {news.map((item, index) => (
                    <li key={index}>
                        <a href={item.url} target="_blank" rel="noopener noreferrer">
                            {item.headline}
                        </a>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default NewsFeed;
