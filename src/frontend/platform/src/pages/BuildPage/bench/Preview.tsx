import { Button } from "@/components/bs-ui/button";
import { Dialog, DialogContent, DialogTitle } from "@/components/bs-ui/dialog";
import { useState } from "react";
import { useTranslation } from "react-i18next";


export default function Preview({ onBeforView }) {
        const { t } = useTranslation()
    const [open, setOpen] = useState(false)
    // 本地开发环境直接访问 client 应用（4001 端口）
    const benchUrl = window.location.hostname === 'localhost' 
        ? 'http://localhost:4001/workspace/' 
        : location.origin + '/workspace/';

    const handleClick = async () => {
        const res = await onBeforView()
        if (res) {
            setOpen(true)
        }
    }

    return <Dialog onOpenChange={setOpen} open={open} >
        <Button variant="outline" className="bg-gray-50 dark:bg-gray-700" onClick={handleClick}>{t('chatConfig.savePreview')}</Button>
        <DialogContent className="max-w-[90vw] h-[90vh]">
            <DialogTitle className="sr-only">预览</DialogTitle>
            <div className="grid gap-4 py-4">
                {open && <iframe src={benchUrl} className="size-full"></iframe>}
            </div>
        </DialogContent>
    </Dialog>
};
