"use client";

import React, { useState, useMemo, useEffect } from 'react';
import { Search, ChevronRight, Hash, ChevronLeft, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { GlossaryTerm } from '@/types';
import glossaryDataRaw from '@/data/glossary.json';

const glossaryData = glossaryDataRaw as GlossaryTerm[];

// Colors from toushibu-official.com analysis
const COLORS = {
    navy: '#1a4696',
    orange: '#ff931e',
    lightBlue: '#dcf0fa',
    textGray: '#444444',
    borderGray: '#e5e7eb',
};

const INITIALS = [
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    'さ', 'し', 'す', 'せ', 'そ',
    'た', 'ち', 'つ', 'て', 'と',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    'ま', 'み', 'む', 'め', 'も',
    'や', 'ゆ', 'よ',
    'ら', 'り', 'る', 'れ', 'ろ',
    'わ', 'A-Z'
];

function TermCard({ item, onClick }: { item: GlossaryTerm, onClick: () => void }) {
    return (
        <div
            className="flex flex-col bg-white border border-slate-200 rounded-xl p-6 transition-all hover:border-[#1a4696]/30 hover:shadow-md cursor-pointer h-[280px]"
            onClick={onClick}
        >
            <div className="mb-4">
                <span className="text-xs font-bold text-[#1a4696] uppercase tracking-wide mb-1 block">
                    {item.reading}
                </span>
                <h3 className="text-2xl font-bold text-[#1a4696] leading-tight line-clamp-2">
                    {item.term}
                </h3>
            </div>

            <div className="flex-grow">
                <p className="text-[#444444] text-lg leading-relaxed font-medium line-clamp-3">
                    {item.definition}
                </p>
                <div className="mt-3 text-sm font-bold text-[#1a4696] flex items-center justify-end">
                    <span className="flex items-center bg-slate-50 px-3 py-1.5 rounded-full hover:bg-slate-100 transition-colors">
                        もっと見る
                    </span>
                </div>
            </div>

            <div className="mt-auto pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-slate-400">
                <span className="bg-slate-50 px-2 py-1 rounded border border-slate-100">
                    索引: {item.initial}
                </span>
            </div>
        </div>
    );
}

export default function GlossaryUI() {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedInitial, setSelectedInitial] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedTerm, setSelectedTerm] = useState<GlossaryTerm | null>(null);
    const ITEMS_PER_PAGE = 100;

    const filteredData = useMemo(() => {
        return glossaryData.filter((item) => {
            const matchesSearch =
                item.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
                item.reading.includes(searchQuery) ||
                item.definition.toLowerCase().includes(searchQuery.toLowerCase());

            const matchesInitial = !selectedInitial ||
                (selectedInitial === 'A-Z'
                    ? /^[A-Za-z]/.test(item.reading)
                    : item.initial === selectedInitial);

            return matchesSearch && matchesInitial;
        });
    }, [searchQuery, selectedInitial]);

    // Reset page when filters change
    useMemo(() => {
        setCurrentPage(1);
    }, [searchQuery, selectedInitial]);

    useEffect(() => {
        if (selectedTerm) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [selectedTerm]);

    const totalPages = Math.ceil(filteredData.length / ITEMS_PER_PAGE);
    const paginatedData = useMemo(() => {
        const start = (currentPage - 1) * ITEMS_PER_PAGE;
        return filteredData.slice(start, start + ITEMS_PER_PAGE);
    }, [filteredData, currentPage]);

    const scrollToTop = () => {
        window.scrollTo(0, 0);
    };

    return (
        <div className="max-w-[1400px] mx-auto px-4 py-8">
            {/* Search Section - Professional & Clean */}
            <div className="bg-[#f8fafc] p-6 rounded-2xl mb-10 border border-[#e2e8f0]">
                <div className="relative max-w-3xl mx-auto">
                    <div className="bg-white border-2 border-[#1a4696] rounded-xl flex items-center px-4 shadow-sm">
                        <Search className="h-6 w-6 text-[#1a4696]" />
                        <input
                            type="text"
                            className="w-full bg-transparent border-0 focus:ring-0 text-slate-900 py-3 px-3 text-xl placeholder-slate-400"
                            placeholder="調べたい用語を入力..."
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value);
                                if (e.target.value) setSelectedInitial(null);
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Initials Filter - Balanced size with brand colors */}
            <div className="mb-10">
                <div className="flex flex-wrap justify-center gap-2">
                    <button
                        onClick={() => {
                            setSelectedInitial(null);
                            setSearchQuery('');
                        }}
                        className={cn(
                            "px-6 py-2 rounded-lg text-lg font-bold transition-all border-2",
                            !selectedInitial
                                ? "bg-[#1a4696] border-[#1a4696] text-white shadow-md"
                                : "bg-white border-slate-200 text-slate-600 hover:border-[#1a4696] hover:text-[#1a4696]"
                        )}
                    >
                        すべて
                    </button>
                    {INITIALS.map((initial) => (
                        <button
                            key={initial}
                            onClick={() => {
                                setSelectedInitial(initial);
                                setSearchQuery('');
                            }}
                            className={cn(
                                "w-12 h-12 flex items-center justify-center rounded-lg text-lg font-bold transition-all border-2",
                                selectedInitial === initial
                                    ? "bg-[#1a4696] border-[#1a4696] text-white shadow-md"
                                    : "bg-white border-slate-200 text-slate-600 hover:border-[#1a4696] hover:text-[#1a4696]"
                            )}
                        >
                            {initial}
                        </button>
                    ))}
                </div>
            </div>

            {/* Results Header */}
            <div className="mb-8 flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-200 pb-4">
                <div className="flex items-center space-x-2">
                    <Hash className="h-5 w-5 text-[#1a4696]" />
                    <span className="text-xl font-bold text-slate-800">
                        検索結果: <span className="text-[#1a4696]">{filteredData.length.toLocaleString()}</span> 件
                    </span>
                    {totalPages > 1 && (
                        <span className="ml-4 text-sm font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
                            {currentPage} / {totalPages} ページ
                        </span>
                    )}
                </div>

                {totalPages > 1 && (
                    <div className="flex items-center gap-2">
                        <button
                            disabled={currentPage === 1}
                            onClick={() => {
                                setCurrentPage(prev => Math.max(1, prev - 1));
                                scrollToTop();
                            }}
                            className="px-4 py-2 text-sm font-bold rounded-lg border border-slate-300 bg-white text-slate-700 disabled:opacity-30 hover:bg-slate-50 transition-colors"
                        >
                            前へ
                        </button>
                        <button
                            disabled={currentPage === totalPages}
                            onClick={() => {
                                setCurrentPage(prev => Math.min(totalPages, prev + 1));
                                scrollToTop();
                            }}
                            className="px-4 py-2 text-sm font-bold rounded-lg bg-[#ff931e] text-white shadow-sm disabled:opacity-30 hover:bg-[#e6841a] transition-colors"
                        >
                            次へ
                        </button>
                    </div>
                )}
            </div>

            {/* Terms Grid - Moderately large, high contrast, branded */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                {paginatedData.map((item) => (
                    <TermCard key={item.id} item={item} onClick={() => setSelectedTerm(item)} />
                ))}
            </div>

            {/* Pagination Bottom */}
            {totalPages > 1 && (
                <div className="mt-16 flex flex-col items-center py-10 border-t border-slate-100">
                    <div className="flex items-center gap-4">
                        <button
                            disabled={currentPage === 1}
                            onClick={() => {
                                setCurrentPage(prev => Math.max(1, prev - 1));
                                scrollToTop();
                            }}
                            className="flex items-center gap-2 px-6 py-3 rounded-lg text-lg font-bold border-2 border-slate-200 bg-white text-slate-600 disabled:opacity-20 hover:bg-slate-50 transition-all active:translate-y-px"
                        >
                            <ChevronLeft className="h-5 w-5" /> 前の100件
                        </button>

                        <div className="flex items-center space-x-2 px-4 py-2 bg-[#1a4696] rounded-lg text-white font-bold">
                            <span>{currentPage}</span>
                            <span className="opacity-50">/</span>
                            <span>{totalPages}</span>
                        </div>

                        <button
                            disabled={currentPage === totalPages}
                            onClick={() => {
                                setCurrentPage(prev => Math.min(totalPages, prev + 1));
                                scrollToTop();
                            }}
                            className="flex items-center gap-2 px-6 py-3 rounded-lg text-lg font-bold bg-[#ff931e] text-white shadow-md disabled:opacity-20 hover:bg-[#e6841a] transition-all hover:translate-y-[-1px] active:translate-y-0"
                        >
                            次の100件 <ChevronRight className="h-5 w-5" />
                        </button>
                    </div>
                    <p className="mt-6 text-sm font-bold text-slate-500">
                        {filteredData.length.toLocaleString()} 件中 {((currentPage - 1) * ITEMS_PER_PAGE + 1).toLocaleString()} 〜 {Math.min(currentPage * ITEMS_PER_PAGE, filteredData.length).toLocaleString()} 件を表示
                    </p>
                </div>
            )}

            {/* Empty State */}
            {filteredData.length === 0 && (
                <div className="mt-20 text-center py-20 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
                    <Search className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold text-slate-800 mb-2">見つかりませんでした</h3>
                    <p className="text-slate-500 max-w-sm mx-auto">
                        キーワードを変えてもう一度お試しください。
                    </p>
                </div>
            )}

            {/* Modal Overlay */}
            {selectedTerm && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
                    onClick={() => setSelectedTerm(null)}>
                    <div
                        className="bg-white rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex items-start justify-between p-6 md:p-8 border-b border-slate-100 bg-slate-50">
                            <div>
                                <span className="text-sm font-bold text-[#1a4696] uppercase tracking-wide mb-2 block">
                                    {selectedTerm.reading}
                                </span>
                                <h2 className="text-2xl md:text-3xl font-bold text-[#1a4696] leading-tight">
                                    {selectedTerm.term}
                                </h2>
                            </div>
                            <button
                                onClick={() => setSelectedTerm(null)}
                                className="p-2 rounded-full hover:bg-slate-200 text-slate-500 transition-colors shrink-0"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>
                        <div className="p-6 md:p-8 overflow-y-auto">
                            <p className="text-[#444444] text-xl leading-relaxed font-medium whitespace-pre-wrap">
                                {selectedTerm.definition}
                            </p>
                        </div>
                        <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-between items-center">
                            <span className="bg-white px-3 py-1.5 rounded-md border border-slate-200 text-sm font-bold text-slate-500">
                                索引: {selectedTerm.initial}
                            </span>
                            <button
                                onClick={() => setSelectedTerm(null)}
                                className="px-6 py-2 bg-[#1a4696] text-white font-bold rounded-lg hover:bg-[#12316e] transition-colors"
                            >
                                閉じる
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
